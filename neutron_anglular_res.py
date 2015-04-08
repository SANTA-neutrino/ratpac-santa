import sys
import ROOT
ROOT.gSystem.Load('libRATEvent')
from ROOT.RAT import DSReader, TrackNav, TrackCursor
ROOT.gStyle.SetOptStat(0)

inputfile = "test.root"
if len(sys.argv)>=2:
    inputfile = sys.argv[1]

reader = DSReader(inputfile) # scintillation+reflections
nevents = reader.GetTotal()
if nevents>400:
    nevents = 400

print "MC file has ",nevents,"events"

out = ROOT.TFile('output_test.root','recreate')

hncos = ROOT.TH1D("hncos","cos of neutron initial direction and final position",100,-1.0,1.0)

for iev in xrange(0,nevents):
    if iev%10==0:
        print "Event ",iev

    dsroot = reader.NextEvent()
    mc = dsroot.GetMC()
    nav = TrackNav(dsroot)
    cursor = nav.Cursor(False)
    
    # follow positron: (1) did it make it drift volume?
    # find capture point
    #tracknode = cursor.GoChild(0)
    #next_tracknode = tracknode
    #positron_escaped = False
    #while next_tracknode!=None:
    #    tracknode = next_tracknode
    #    vol = tracknode.GetVolume()
    #    if vol=="volDrift_PV":
    #        #print "positron makes it to drift layer with KE=",tracknode.GetKE()," MeV"
    #        positron_escaped = True
    #        break
    #    next_tracknode = cursor.GoNext()
    #
    #if not positron_escaped:
    #    #print "final positron position: ",tracknode.GetEndpoint().X(),tracknode.GetEndpoint().Y(),tracknode.GetEndpoint().Z()," process=",tracknode.GetProcess()
    #    pass
    #cursor.GoParent()
    #cursor.GoTrackStart()

    tracknode = cursor.GoChild(1) # neutron
    n_pos = tracknode.GetEndpoint()
    n_mom = tracknode.GetMomentum()
    n_initdir = n_mom.Unit()
    #print "neutron initial momentum: ",n_mom.X(),n_mom.Y(),n_mom.Z()
    #print "neutron initial dir: ",n_initdir.X(),n_initdir.Y(),n_initdir.Z()

    tracknode = cursor.GoTrackEnd()
    n_endpos = tracknode.GetEndpoint()
    n_diff = n_endpos-n_pos
    n_dir = n_diff.Unit()
    #print "neutron final position: ",tracknode.GetEndpoint().X(),tracknode.GetEndpoint().Y(),tracknode.GetEndpoint().Z()
    #print "neutron travel direction: ",n_dir.X(),n_dir.Y(),n_dir.Z()
    n_cos = n_dir.X()*n_initdir.X() + n_dir.Y()*n_initdir.Y() + n_dir.Z()*n_initdir.Z()
    print "Neutron travel cos: ",n_cos," last process=",tracknode.GetProcess()
    if tracknode.GetProcess()=="NeutronInelastic":
        hncos.Fill( n_cos )

out.Write()

c = ROOT.TCanvas("c","c",800,600)
c.Draw()
hncos.Draw()
c.Update()
raw_input()
