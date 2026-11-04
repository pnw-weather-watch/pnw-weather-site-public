# NOAA WW3 + NOAA OISST under the Waves tab - 11-03-26 PST (Benjamin t2228u)
Previews: edaf517b, 430d5752 (final). Production 83b7b270 (6b33767), previous 3a382136.
Before: WW3 and OISST products were already Waves-tab products, but their runs sat at the bottom of the one big Runs picker under every
weather model, and the dimmed Waves button (non-wave models) only opened ECMWF (and was hidden in Studio).
Now (viewer + Studio): Runs picker shows the runs for the open tab. Waves tab: ECMWF 0.25 (waves, wavemax, wavemax24), NOAA WW3 (waves, swper,
swellhs), NOAA OISST (ssta) only. Every other tab: weather models only (no WW3 / OISST). The shown run is always listed.
On a WW3 / OISST run, Surface/Precip/Snow/Upper Air/Severe show dimmed in their usual place and open the newest ECMWF run on that tab.
On models without waves the dimmed Waves button opens newest ECMWF Waves (now also in Studio). Compare frames: unchanged (all runs).
Deep links ?model=gfsw, ?model=oisst, ?prod=ssta, ?prod=waves, ?run= all open as before.
QA (desk 1512x945@2x, phone 390x844@3x, Studio 1080x1920/1920x1080; preview + prod): 0 console/page errors, 0 bad responses; scrubber
prev/next/slider OK on WW3 (84 steps) and OISST (14 days, opens newest). Screens: /workspace/waves_tab_qa/pv2/ and prod/.
