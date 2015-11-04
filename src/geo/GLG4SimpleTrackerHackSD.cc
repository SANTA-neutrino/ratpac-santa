// This file is part of the GenericLAND software library.
// $Id: GLG4SimpleTrackerHackSD.cc,v 1.1 2005/08/30 19:55:22 volsung Exp $
//
//  GLG4SimpleTrackerHackSD.cc
//
//   Records total number of hits on each SimpleTrackerHack.
//   Uses Geant4-style hit collection to record hit time, place, etc.
//
//  GLG4 version by Glenn Horton-Smith December, 2004.
//  Based on earlier work by O. Tajima and G. Horton-Smith
//

#include "GLG4SimpleTrackerHackSD.hh"
#include "GLG4VEventAction.hh"

#include "G4Track.hh"
#include "G4Step.hh"
#include "G4HCofThisEvent.hh"
#include "G4TouchableHistory.hh"
#include "G4ios.hh"
#include "G4SDManager.hh"

#include "GLG4Scint.hh"  // for doScintilllation and total energy deposition info
#include "G4VSolid.hh" // for access to solid store
#include "Randomize.hh"
#include <RAT/Log.hh>

#include <string.h>  // for memset

GLG4SimpleTrackerHackSD::GLG4SimpleTrackerHackSD(G4String name, int arg_max_trackers, int arg_tracker_no_offset )
:G4VSensitiveDetector(name)
{
  max_trackerchs= arg_max_trackers;
  tracker_no_offset= arg_tracker_no_offset;
  my_id_tracker_size= 0;
  
  hit_sum= new G4int[max_trackerchs];
}

GLG4SimpleTrackerHackSD::~GLG4SimpleTrackerHackSD()
{
  if (hit_sum)
    delete[] hit_sum;
}


void GLG4SimpleTrackerHackSD::Initialize(G4HCofThisEvent*)
{
  memset(hit_sum, 0, sizeof(hit_sum[0])*max_trackerchs);
  n_tracker_hits= n_hit_trackerchs= 0;
}


G4bool GLG4SimpleTrackerHackSD::ProcessHits(G4Step* aStep, G4TouchableHistory* hist)
{

  G4double ke = aStep->GetTotalEnergyDeposit(); /// we've hacked this --- This is the energy deposited!!!!
  if ( ke<=0 )
    return false;

  // things to do:
  // (1) get optical ID number (means we need system of indexing!)
  // (2) get track info
  // (3) call SimpleHit
  // (4) kill photon

  // get optical id
  G4StepPoint* prestep = aStep->GetPreStepPoint();
  G4VPhysicalVolume* pv = prestep->GetPhysicalVolume();
  int channelid = pv_to_channelid_map[pv];
  G4double time = aStep->GetTrack()->GetGlobalTime();
  G4ThreeVector pos = aStep->GetTrack()->GetPosition();
  G4ThreeVector mom = aStep->GetTrack()->GetMomentum();
  G4ThreeVector pol = aStep->GetTrack()->GetPolarization();
  G4int N_pe = 1;
  G4int trackid = aStep->GetTrack()->GetTrackID();
  G4bool prepulse = false;
  int origin_flag = aStep->GetTrack()->GetDefinition()->GetPDGEncoding();
  
  RAT::info << "GLG4SimpleTrackerHackSD detects " << aStep->GetTrack()->GetDefinition()->GetParticleName () << " in Channel " << channelid << "!" << newline;
  SimpleHit( channelid, time, ke, pos, mom, pol, N_pe, trackid, origin_flag, prepulse );
  
  return true;
}


// Here is the real "hit" routine, used by GLG4SimpleTrackerHackOpticalModel and by ProcessHits
// It is more efficient in some ways.
void GLG4SimpleTrackerHackSD::SimpleHit( G4int itracker,
				   G4double time,
				   G4double kineticEnergy,
				   const G4ThreeVector &hit_position,
				   const G4ThreeVector &hit_momentum,
				   const G4ThreeVector &hit_polarization,
				   G4int iHitPhotonCount,
				   G4int trackID,
				   G4int origin_flag,
				   G4bool prepulse )
{
  G4int tracker_index = channelid_to_trackerindex[itracker]-tracker_no_offset;
  if (tracker_index < 0 || tracker_index >= max_trackerchs)
    {
      G4cerr << "Error: GLG4SimpleTrackerHackSD::SimpleHit [" << GetName() << "] passed itracker="
	     << itracker << ", but max_trackerchs=" << max_trackerchs
	     << " and offset=" << tracker_no_offset << " !" << G4endl;
      return;
    }
  
  hit_sum[tracker_index]+= iHitPhotonCount;

  // create new GLG4HitPhoton, the way of recording photo hits on SimpleTrackerHacks
  GLG4HitPhoton* hit_photon = new GLG4HitPhoton();
  hit_photon->SetPMTID((int)itracker);
  hit_photon->SetTime((double) time );
  hit_photon->SetKineticEnergy((double) kineticEnergy );
  hit_photon->SetPosition( 
			  (double)hit_position.x(),
			  (double)hit_position.y(),
			  (double)hit_position.z()
			  );
  hit_photon->SetMomentum( 
			  (double)hit_momentum.x(),
			  (double)hit_momentum.y(),
			  (double)hit_momentum.z()
			  );
  hit_photon->SetPolarization( 
			      (double)hit_polarization.x(),
			      (double)hit_polarization.y(),
			      (double)hit_polarization.z()
			      );
  hit_photon->SetCount( iHitPhotonCount );
  hit_photon->SetTrackID( trackID );
  hit_photon->SetPrepulse( prepulse );
  hit_photon->SetOriginFlag( origin_flag );
    
  GLG4VEventAction::GetTheHitPMTCollection()->DetectPhoton(hit_photon); // we still use the PMT hit collection.
}


void GLG4SimpleTrackerHackSD::EndOfEvent(G4HCofThisEvent*)
{
  int itracker;
    
  n_tracker_hits=0;
  n_hit_trackerchs=0;
  for (itracker=0; itracker<max_trackerchs; itracker++) {
    if (hit_sum[itracker]) {
      n_tracker_hits+= hit_sum[itracker];
      n_hit_trackerchs++;
    }
  }

}


void GLG4SimpleTrackerHackSD::clear()
{} 

void GLG4SimpleTrackerHackSD::DrawAll()
{}

void GLG4SimpleTrackerHackSD::PrintAll()
{
}
