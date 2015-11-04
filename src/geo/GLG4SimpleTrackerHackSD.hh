// This file is part of the GenericLAND software library.
// $Id: GLG4PMTSD.hh,v 1.1 2005/08/30 19:55:22 volsung Exp $
//
//  GLG4SimpleTrackerHackSD.hh
//
//   Copy of GLG4PMTSD. We've hijacked the PMT sensitive detector system!!
//   We create "photon hits", to record energy depositions in our tracker.
//   Forgive me.
//
//   Blame T. Wongjirad: 2015/11/04
//

#ifndef GLG4SimpleTrackerHackSD_h
#define GLG4SimpleTrackerHackSD_h 1

#include "G4VSensitiveDetector.hh"
#include "G4VPhysicalVolume.hh"
#include <map>

class G4Step;
class G4HCofThisEvent;
class G4TouchableHistory;

class GLG4SimpleTrackerHackSD : public G4VSensitiveDetector
{
  protected:
      int max_trackerchs;
      int tracker_no_offset;
      int my_id_tracker_size;
      // enum { max_waveform_ns= 200 };

  std::map< int, G4VPhysicalVolume* > channelmap;
  std::map< G4VPhysicalVolume*, int > pv_to_channelid_map;
  std::map< int, int > channelid_to_trackerindex; /// need to go from ID number (arbitrary) to trackerindex;
  
  public:
      G4int *hit_sum;  /* indexed by tracker number */
      //typedef G4int waveform_t[max_waveform_ns];
      //waveform_t *hit_waveform; /* indexed by tracker number */
  
      G4int n_tracker_hits;   /* # of hits,       calculated at EndOfEvent */
      G4int n_hit_trackerchs;   /* # of Trackerchs hit,   calculated at EndOfEvent */

  public:
  // member functions
      GLG4SimpleTrackerHackSD(G4String name,
			int max_trackerchs=1000000,
			int tracker_no_offset=0 );
      virtual ~GLG4SimpleTrackerHackSD();

      virtual void Initialize(G4HCofThisEvent*HCE);
      virtual void EndOfEvent(G4HCofThisEvent*HCE);
      virtual void clear();
      virtual void DrawAll();
      virtual void PrintAll();

      void SimpleHit( G4int itracker,
		      G4double time,
		      G4double kineticEnergy,
		      const G4ThreeVector & position,
		      const G4ThreeVector & momentum,
		      const G4ThreeVector & polarization,
		      G4int iHitPhotonCount,
		      G4int origin_flag,
		      G4int trackID=-1,
		      G4bool prepulse=false );
  
  void AddTrackerChannel( int idnum, G4VPhysicalVolume* pv ) { 
    channelmap[idnum] = pv; 
    pv_to_channelid_map[pv] = idnum; 
    channelid_to_trackerindex[idnum] = my_id_tracker_size;
    my_id_tracker_size++;
  };
  protected:
      virtual G4bool ProcessHits(G4Step*aStep,G4TouchableHistory*ROhist);
};

#endif
