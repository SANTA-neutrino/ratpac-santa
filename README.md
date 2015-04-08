
# SANTA RAT Fork

Simulation code for SANTA.

## Checking out

* using git flow pattern (more info: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
* git clone https://github.com/twongjirad/ratpac-kpipe.git
* git checkout develop (this moves you to the develop branch)

## Dependencies
* ROOT 5
* Geant4 (checked things worked with geant4.6.p04)
* scons

## building
* instructions in doc/installation.rst
* make sure ROOT and geant4 environment variables set
* ./configure
* scons

## Running
* rat
* /control/execute mac/santa.mac (will bring up and initialize geometry)

## Adding a feature
* git checkout develop
* git checkout -b [username]_[featurename]
* do something awesome
* to put your code onto develop: git checkout develop; git merge [username]_[featurename]
* delete the branch

## Geometry

* in data/santa/santa.gdml

![alt tag](https://raw.github.com/SANTA-neutrino/ratpac-santa/master/data/santa/santa_gdml.png)


## Optical Detector

* Needed to add new type of Sensitive Detector class for optical detectors
* RAT optical detectors too tied to PMTs
* Created GLG4SimpleOpDetSD.  No fancy physics. If opticalphoton hits it, then a hit gets made. (later we can maybe configure this.)
* To add it, include opdet_lv_name in GEO RAT db table.
* Also, in GDML give each physvol instance a name with a number. This number will be used to assign the opdet a channel number.
* example:
```
[In GEO table]
{
name: "GEO",
valid_begin: [0, 0],
valid_end: [0, 0],
gdml_file: "kpipe.gdml",
opdet_lv_name: "volSiPM",
}

[in GDML file]
...
    <physvol name="OpDet1">
      <volumeref ref="volSiPM"/>
      <position name="posSiPM1" unit="cm" x="0" y="0" z="0"/>
    </physvol>
    <physvol name="OpDet2">
      <volumeref ref="volSiPM"/>
      <position name="posSiPM2" unit="cm" x="0" y="0" z="10"/>
    </physvol>
...
```


# RAT (is an Analysis Tool), Public Edition
-----------------------------------------
RAT is a simulation and analysis package built with GEANT4, ROOT, and C++,
originally developed by S. Seibert for the Braidwood Collaboration. Versions
of RAT are now being used and developed by several particle physics
experiments.

RAT combines simulation and analysis into a single framework, which allows
analysis code to trivially access the same detector geometry and physics
parameters used in the detailed simulation.

RAT follows the "AMARA" principle: As Microphysical as Reasonably Achievable.
Each and every photon is tracked through an arbitrarily detailed detector
geometry, using standard GEANT4 or custom physics processes. PMTs are fully
modeled, and detected photons may be propagated to a simulation of front-end
electronics and DAQ.

This generic version is intended as a starting point for collaborations
looking for an easy-to-learn, extensible detector simulation and analysis
package that works out of the box. Once acquainted with RAT, it is easy to
customize the geometry elements, physics details, data structure, analysis
tools, etc., to suit your experiment's needs.

## Example IBD event

Here shows the steps of particles resulting from an IBD event. 
This also shows the commands to use the navigator.

```
Taritreees-MacBook-Pro:ratpac-santa twongjirad$ root
RAT: Libraries loaded.
root [0] 
root [1] RAT::DSReader* ds = new RAT::DSReader("test.root");
root [2] r = ds->NextEvent(); RAT::TrackNav nav(r); RAT::TrackCursor c = nav.Cursor(true)
Track 0: TreeStart
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
* 0. (   0.0,   0.0,   0.0)      _____ <0.001                 ->e+(1),neutron(2)
(class RAT::DS::Root*)0x7fa23e4c14e0
root [3] c.GoChild(1)
Track 2: neutron  parent: TreeStart(0)
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
* 0. (   0.0,   0.0,   0.0) volTarget_PV  0.008           start 
  1. (  -0.8,  -0.8,   2.0) volTarget_PV  0.008      hadElastic 
  2. (  -1.3,  -1.2,   2.8) volTarget_PV  0.001      hadElastic ->proton(3)
  3. (   0.1,  -1.8,   5.0) volTarget_PV  0.001  Transportation 
  4. (  41.6, -19.9,  70.0) volDrift_PV  0.001  Transportation 
  5. (  47.6, -22.5,  79.3) pvCaptureForward <0.001      hadElastic 
  6. (  94.4, -29.0,  83.2) pvCaptureForward <0.001      hadElastic 
  7. (  97.9, -28.0,  87.8) pvCaptureForward <0.001      hadElastic 
  8. ( 104.4, -26.4,  90.6) pvCaptureForward <0.001      hadElastic 
  9. ( 105.0, -25.5,  90.9) pvCaptureForward <0.001      hadElastic 
 10. ( 105.0, -25.5,  90.9) pvCaptureForward <0.001      hadElastic 
 11. ( 101.1, -31.4,  93.7) pvCaptureForward <0.001      hadElastic 
 12. ( 100.7, -33.2, 100.9) pvCaptureForward <0.001      hadElastic 
 13. ( 120.0, -52.0, 129.5) pvCaptureForward <0.001      hadElastic 
 14. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001 NeutronInelastic ->3 tracks
(class RAT::TrackNode*)0x7fa23fed6180
root [4] c.GoTrackEnd()
Track 2: neutron  parent: TreeStart(0)
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
  0. (   0.0,   0.0,   0.0) volTarget_PV  0.008           start 
  1. (  -0.8,  -0.8,   2.0) volTarget_PV  0.008      hadElastic 
  2. (  -1.3,  -1.2,   2.8) volTarget_PV  0.001      hadElastic ->proton(3)
  3. (   0.1,  -1.8,   5.0) volTarget_PV  0.001  Transportation 
  4. (  41.6, -19.9,  70.0) volDrift_PV  0.001  Transportation 
  5. (  47.6, -22.5,  79.3) pvCaptureForward <0.001      hadElastic 
  6. (  94.4, -29.0,  83.2) pvCaptureForward <0.001      hadElastic 
  7. (  97.9, -28.0,  87.8) pvCaptureForward <0.001      hadElastic 
  8. ( 104.4, -26.4,  90.6) pvCaptureForward <0.001      hadElastic 
  9. ( 105.0, -25.5,  90.9) pvCaptureForward <0.001      hadElastic 
 10. ( 105.0, -25.5,  90.9) pvCaptureForward <0.001      hadElastic 
 11. ( 101.1, -31.4,  93.7) pvCaptureForward <0.001      hadElastic 
 12. ( 100.7, -33.2, 100.9) pvCaptureForward <0.001      hadElastic 
 13. ( 120.0, -52.0, 129.5) pvCaptureForward <0.001      hadElastic 
*14. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001 NeutronInelastic ->3 tracks
(class RAT::TrackNode*)0x7fa23fed6fb0
root [5] c.GoChild(0)
Track 5: gamma  parent: neutron(2)
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
* 0. ( 120.0, -52.2, 129.7) pvCaptureForward  0.478 NeutronInelastic 
  1. ( 108.5,  15.5,  80.9) pvCaptureForward  0.426           compt ->e-(324)
  2. (  99.8,  23.7,  70.0) pvCaptureForward  0.426  Transportation 
  3. (  47.6,  72.7,   5.0) volDrift_PV  0.426  Transportation 
  4. (  39.5,  80.2,  -5.0) volTarget_PV  0.426  Transportation 
  5. ( -12.7, 129.1, -70.0) volDrift_PV  0.426  Transportation 
  6. ( -16.6, 132.8, -74.8) pvCaptureBackward  0.352           compt ->e-(325)
  7. ( -16.4, 142.6,-130.0) pvCaptureBackward  0.352  Transportation 
  8. ( -13.0, 342.8,-1250.0) volDrift_PV  0.352  Transportation 
  9. (  13.8,1906.9,-10000.0) volWorld_PV  0.352  Transportation 
(class RAT::TrackNode*)0x7fa23fed70b0
root [6] c.GoParent()
root [7] c.GoChild(1)
Track 4: alpha  parent: neutron(2)
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
* 0. ( 120.0, -52.2, 129.7) pvCaptureForward  1.472 NeutronInelastic 
  1. ( 120.0, -52.2, 129.7) pvCaptureForward  0.603         ionIoni 
  2. ( 120.0, -52.2, 129.7) pvCaptureForward  0.180         ionIoni 
  3. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001         ionIoni 
  4. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001 AlphaInTpbScintillation 
(class RAT::TrackNode*)0x7fa23fed8670
root [8] c.GoParent()
root [9] c.GoChild(2)
Track 6: Li7[0.0]  parent: neutron(2)
-----------------------------------------------------------------------------------
 # |          position                |  MeV |     process    |   subtracks
-----------------------------------------------------------------------------------
* 0. ( 120.0, -52.2, 129.7) pvCaptureForward  0.838 NeutronInelastic 
  1. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001         ionIoni 
  2. ( 120.0, -52.2, 129.7) pvCaptureForward <0.001 RadioactiveDecay 
(class RAT::TrackNode*)0x7fa23fed8bd0
```

Neutron goes to capture layer. Undergoes NeutronInelastic and produces gamma, alpha, and Li7.

## Example analysis using truth

Make events. (Note this will need to be replaced by a proper Sensitive detector. Using truth tracks like this is not efficient. 1000 events requires >300 MB file! Not good.)
```
rat mac/ibd_santa.mac -o test.root
```

Then run script
```
python neutron_anglular_res.py test.root
```

Should make something like this:
![alt tag](https://raw.github.com/SANTA-neutrino/ratpac-santa/master/data/santa/n_angular_res.png)