"""One camera per view.

Every static layer (land fill, coastline, towns, buoys) and the data lookup
are built from this object. 0.25 deg values are cell centers: row i is
lat = 90 - i*0.25, column j is lon = j*0.25. Longitudes are mod 360.
The image edge sits half a cell outside the first and last centers.
The browser stacks layers of this size; it does not reproject.
"""
import numpy as np

RES = 0.25

# Places the viewer labels. Coordinates match tools/fast/site/viewer.js.
PLACES = (
    ("town", "Honolulu", 21.3069, -157.8583),
    ("town", "Honolulu", 21.28, -157.84),
    ("town", "Hilo", 19.7297, -155.09),
    ("town", "Hilo", 19.725, -155.07),
    ("town", "Kailua-Kona", 19.64, -155.996),
    ("town", "San Francisco", 37.7749, -122.4194),
    ("town", "San Francisco", 37.76, -122.51),
    ("town", "Seattle", 47.6062, -122.3321),
    ("buoy", "51003", 19.151, -160.617),
    ("buoy", "51002", 17.07, -157.755),
    ("buoy", "51206", 19.779, -154.97),
    ("buoy", "46026", 37.75, -122.838),
    ("buoy", "46059", 38.067, -129.895),
    ("buoy", "46002", 42.56, -130.523),
)


def lon360(lon):
    return np.mod(np.asarray(lon, dtype=float), 360.0)


def cell_ij(lat, lon, res=RES):
    """Cell-center index. lat = 90 - i*res, lon = (j*res) mod 360."""
    return (90.0 - np.asarray(lat, dtype=float)) / res, lon360(lon) / res


def half_cell_edges(centers, res=RES):
    """Edges half a cell outside the first and last center."""
    c = np.asarray(centers, dtype=float)
    return np.concatenate([[c[0] - res / 2.0], (c[:-1] + c[1:]) / 2.0, [c[-1] + res / 2.0]])


class Camera:
    def __init__(self, view, dpi=100):
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        import house_style as HS
        self.ccrs = ccrs
        self.fig = plt.figure(figsize=HS.SCREEN_IN, dpi=dpi)
        self.fig.patch.set_facecolor(HS.BG)
        self.layout = HS.screen_layout(self.fig)
        proj = view["proj"]
        self.ax = self.fig.add_axes(list(self.layout["axes"]), projection=proj)
        if "extent" in view:
            self.ax.set_extent(view["extent"], crs=proj)
        else:
            self.ax.set_extent(view["ll"], crs=ccrs.PlateCarree())
        slot = self.layout["axes"]
        HS.fill_projected_limits(self.ax, slot)
        self.fig.canvas.draw()
        HS.fill_projected_limits(self.ax, slot)
        self.fig.canvas.draw()
        self.xlim = tuple(float(v) for v in self.ax.get_xlim())
        self.ylim = tuple(float(v) for v in self.ax.get_ylim())
        p = self.ax.get_position()
        self.position = (float(p.x0), float(p.y0), float(p.width), float(p.height))
        self._lock()
        self.fig._cam = self
        self.fig._screen = self.layout

    def _lock(self):
        """Cartopy's equal-aspect pass must not move this axes on a later draw."""
        ax, xlim, ylim, pos = self.ax, self.xlim, self.ylim, self.position

        def apply_aspect(position=None):
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_position(pos)

        ax.apply_aspect = apply_aspect

    def snap(self):
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_position(self.position)

    def size(self):
        w, h = self.fig.get_size_inches() * self.fig.dpi
        return float(w), float(h)

    def panel(self):
        """Data rectangle in figure pixels, y from the top. Same rectangle as the axes."""
        W, H = self.size()
        x, y, w, h = self.position
        return [x * W, (1.0 - y - h) * H, w * W, h * H]

    def bounds(self):
        """Projected extent (xmin, xmax, ymin, ymax) shared by every layer."""
        return (self.xlim[0], self.xlim[1], self.ylim[0], self.ylim[1])

    def _fold(self, lon):
        lon = float(lon)
        if lon > 180.0:
            lon -= 360.0
        elif lon < -180.0:
            lon += 360.0
        return lon

    def pixel(self, lon, lat):
        """Figure pixel of a lon/lat. y grows downward. Lon may be -180..180 or 0..360."""
        self.snap()
        x, y = self.ax.projection.transform_point(self._fold(lon), float(lat), self.ccrs.PlateCarree())
        dx, dy = self.ax.transData.transform((x, y))
        _, H = self.size()
        return float(dx), float(H - dy)

    def lonlat(self, x, y):
        """Figure pixel (y from the top) -> (lon mod 360, lat)."""
        self.snap()
        _, H = self.size()
        px, py = self.ax.transData.inverted().transform((float(x), H - float(y)))
        lon, lat = self.ccrs.PlateCarree().transform_point(px, py, self.ax.projection)
        return float(np.mod(lon, 360.0)), float(lat)

    def anchors(self):
        """Town and buoy dots in this figure's pixel space."""
        px, py, pw, ph = self.panel()
        out = []
        for kind, name, lat, lon in PLACES:
            x, y = self.pixel(lon, lat)
            if px - 2 <= x <= px + pw + 2 and py - 2 <= y <= py + ph + 2:
                out.append({"kind": kind, "name": name, "lat": lat, "lon": lon,
                            "x": round(x, 2), "y": round(y, 2)})
        return out

    def close(self):
        import matplotlib.pyplot as plt
        plt.close(self.fig)


def sample_grid(cam, stride, res=RES):
    """One lookup grid for this camera. fi, fj are cell-center indices, lon mod 360."""
    px, py, pw, ph = cam.panel()
    x0, x1, y0, y1 = cam.bounds()
    nx = int(np.ceil(pw / stride)) + 1
    ny = int(np.ceil(ph / stride)) + 1
    gxp = np.arange(nx) * stride
    gyp = np.arange(ny) * stride
    PX = x0 + (gxp[None, :] / pw) * (x1 - x0) + 0.0 * gyp[:, None]
    PY = y1 - (gyp[:, None] / ph) * (y1 - y0) + 0.0 * gxp[None, :]
    proj = cam.ax.projection
    pc = cam.ccrs.PlateCarree()
    ll = pc.transform_points(proj, PX, PY)
    LO, LA = ll[..., 0], ll[..., 1]
    fi, fj = cell_ij(LA, LO, res)
    n2 = proj.transform_points(pc, np.where(LO > 180.0, LO - 360.0, LO), np.minimum(LA + 0.05, 89.9))
    ang = np.arctan2(-(n2[..., 1] - PY) / (y1 - y0) * ph, (n2[..., 0] - PX) / (x1 - x0) * pw)
    return {"fi": fi, "fj": fj, "ang": ang, "nx": nx, "ny": ny,
            "px": px, "py": py, "pw": pw, "ph": ph, "lon": lon360(LO), "lat": LA}
