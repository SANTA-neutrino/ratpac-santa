import sys
import ROOT
ROOT.gSystem.Load('libRATEvent')
from ROOT.RAT import DSReader, TrackNav, TrackCursor
ROOT.gStyle.SetOptStat(0)
import sys, os


#inputfile = "test.root"
if len(sys.argv)==2:
    inputfile = sys.argv[1]
    tag = 'test'
#    inputfile = sys.argv[1]
elif len(sys.argv)==3:
    inputfile = sys.argv[1]
    tag = sys.argv[2]
else:
    inputfile = "test.root"
    tag = 'test'

print 'The input file is ', inputfile, '. And the tag is ', tag


reader = DSReader(inputfile) # scintillation+reflections
nevents = reader.GetTotal()
#if nevents>400:
#    nevents = 400

print "MC file has ",nevents,"events"

out = ROOT.TFile('output_test.root','recreate')

hncos = ROOT.TH1D("hncos","cos of neutron initial direction and final position",100,-1.0,1.0)

hpcos = ROOT.TH1D("hpcos","cos of positron initial direction and direction in drift layer",100,-1.0,1.0)

hnucoswp = ROOT.TH1D("hnucoswp","cos of antineutrino initial and reconstructed directions, using positrons",100,-1.0,1.0)

hnucosnp = ROOT.TH1D("hnucosnp","cos of antineutrino initial and reconstructed directions, without positrons",100,-1.0,1.0)


##tag for data storage
#tag = 'April17'

#make dirs
data_dir = 'analysis/data/'
data_dir_tag = data_dir + tag + '/'
dirs = [data_dir,data_dir_tag]

def make_dirs():
    for d in dirs:
        if not os.path.exists(d):
            os.mkdir(d)

make_dirs()


#==============================
#Initilize arrays
positron_rec_dir_vector = []
neutron_rec_dir_vector = []
positron_true_dir_vector = []
neutron_true_dir_vector = []
positron_energy_vector = []
positron_energy_gap_vector = []
capture_time_vec = []
ibd_pos_vector = []




#==============================
#Scan through all events
for iev in xrange(0,nevents):
    if iev%10==0:
        print "Event ",iev

    dsroot = reader.NextEvent()
    mc = dsroot.GetMC()
    nav = TrackNav(dsroot)
    cursor = nav.Cursor(False)
    
    #follow positron: (1) did it make it drift volume?
    #find capture point
    tracknode = cursor.GoChild(0) #the positron
    #annode = cursor.GoParent() #the antineutrino

    p_pos = tracknode.GetEndpoint()
    p_mom = tracknode.GetMomentum()
    p_initdir = p_mom.Unit()
    p_initE = tracknode.GetKE()
    time_0 = tracknode.GetGlobalTime()
    next_tracknode = tracknode
    positron_escaped = False
    while next_tracknode!=None:
        tracknode = next_tracknode
        vol = tracknode.GetVolume()
        if vol=="volDrift_PV":
            print "positron makes it to drift layer with KE=",tracknode.GetKE()," MeV"
            print "The inital KE = ", p_initE, " MeV"
            print "Positron makes it out in ", tracknode.GetGlobalTime() - time_0, " ns"
            p_mom_end = tracknode.GetMomentum().Unit()
            p_cos = p_mom_end.X()*p_initdir.X() + p_mom_end.Y()*p_initdir.Y() + p_mom_end.Z()*p_initdir.Z()
            hpcos.Fill(p_cos)
            print "positron cos = ", p_cos
            positron_escaped = True
            
            positron_momentum = [p_mom_end.X(), p_mom_end.Y(), p_mom_end.Z()]
            E_positron_gap = tracknode.GetKE()
            
            
            break
        next_tracknode = cursor.GoNext()
    
    if not positron_escaped:
        #print "final positron position: ",tracknode.GetEndpoint().X(),tracknode.GetEndpoint().Y(),tracknode.GetEndpoint().Z()," process=",tracknode.GetProcess()
        positron_momentum = [0,0,0]
        E_positron_gap = 0
        
        pass


    #now do the neutron
    cursor.GoParent()
    cursor.GoTrackStart()

    tracknode = cursor.GoChild(1) # neutron
    n_pos = tracknode.GetEndpoint()
    n_mom = tracknode.GetMomentum()
    an_mom = p_mom + n_mom #antineutrino momentum
    n_initdir = n_mom.Unit()
    n_true_dir = [n_initdir.X(),n_initdir.Y(), n_initdir.Z()]
    #print "neutron initial momentum: ",n_mom.X(),n_mom.Y(),n_mom.Z()
    #print "neutron initial dir: ",n_initdir.X(),n_initdir.Y(),n_initdir.Z()

    tracknode = cursor.GoTrackEnd()
    n_endpos = tracknode.GetEndpoint()
    n_diff = n_endpos-n_pos
    n_dir = n_diff.Unit()

    ibd_pos = [n_pos.X(),n_pos.Y(),n_pos.Z()]

    print 'The initial neutron position is ', [n_pos.X(),n_pos.Y(), n_pos.Z()]

    #print "neutron final position: ",tracknode.GetEndpoint().X(),tracknode.GetEndpoint().Y(),tracknode.GetEndpoint().Z()
    #print "neutron travel direction: ",n_dir.X(),n_dir.Y(),n_dir.Z()
    n_cos = n_dir.X()*n_initdir.X() + n_dir.Y()*n_initdir.Y() + n_dir.Z()*n_initdir.Z()

    print "Neutron travel cos: ",n_cos," last process=",tracknode.GetProcess()
    print 'The volume is ', tracknode.GetVolume()
    time_stamp_neutron = tracknode.GetGlobalTime() - time_0
    if (tracknode.GetProcess()=="NeutronInelastic" or tracknode.GetProcess()=="nCapture") and (tracknode.GetVolume() == "pvCaptureForward" or tracknode.GetVolume() == "pvCaptureBackward"): # and time_stamp_neutron > t_min and time_stamp_neutron < t_max :
        print "The volume is ", tracknode.GetVolume()
        print "Neutron is captured in ", tracknode.GetGlobalTime() - time_0, " ns"
        print "The initial antineutrino direction is ", (an_mom.X(),an_mom.Y(),an_mom.Z())
        hncos.Fill( n_cos )

        neutron_rec_dir = [n_dir.X(),n_dir.Y(), n_dir.Z()]
    else:
        neutron_rec_dir = [0, 0, 0]
        time_stamp_neutron = 0

    #fill arrays
    positron_energy_vector.append(p_initE)
    positron_energy_gap_vector.append(E_positron_gap)
    positron_true_dir_vector.append([p_initdir.X(),p_initdir.Y(),p_initdir.Z()])
    positron_rec_dir_vector.append(positron_momentum)
    capture_time_vec.append(time_stamp_neutron)
    neutron_rec_dir_vector.append(neutron_rec_dir)
    neutron_true_dir_vector.append(n_true_dir)
    ibd_pos_vector.append(ibd_pos)

import json, pickle

#print 'An exampe vector is ', positron_true_dir_vector

file_positron_energy_vector = open(data_dir_tag+'positron_energy_vector-'+tag+'.json','w+')
file_positron_energy_gap_vector = open(data_dir_tag+'positron_energy_gap_vector-'+tag+'.json','w+')
file_positron_true_dir_vector = open(data_dir_tag+'positron_true_dir_vector-'+tag+'.json','w+')
file_positron_rec_dir_vector = open(data_dir_tag+'positron_rec_dir_vector-'+tag+'.json','w+')
file_capture_time_vec = open(data_dir_tag+'capture_time_vec-'+tag+'.json','w+')
file_neutron_rec_dir_vector = open(data_dir_tag+'neutron_rec_dir_vector-'+tag+'.json','w+')
file_neutron_true_dir_vector = open(data_dir_tag+'neutron_true_dir_vector-'+tag+'.json','w+')
file_ibd_pos_vector = open(data_dir_tag+'ibd_pos_vector-'+tag+'.json','w+')


files = [file_positron_energy_vector, file_positron_energy_gap_vector, file_positron_true_dir_vector, file_positron_rec_dir_vector, file_capture_time_vec, file_neutron_rec_dir_vector, file_neutron_true_dir_vector,file_ibd_pos_vector]

data = [positron_energy_vector, positron_energy_gap_vector, positron_true_dir_vector, positron_rec_dir_vector, capture_time_vec, neutron_rec_dir_vector, neutron_true_dir_vector,ibd_pos_vector]

for i in range(len(files)):
    with files[i] as f:
        pickle.dump(data[i], f) #, indent=2)

#json.dump(positron_energy_vector, file_positron_energy_vector)
#json.dump(positron_energy_gap_vector, file_positron_energy_gap_vector)
#json.dump(positron_true_dir_vector, file_positron_true_dir_vector)
#json.dump(positron_rec_dir_vector, file_positron_rec_dir_vector)
#json.dump(capture_time_vec, file_capture_time_vec)
#json.dump(neutron_rec_dir_vector, file_neutron_rec_dir_vector)
#json.dump(neutron_true_dir_vector, file_neutron_true_dir_vector)

#np.save('analysis/positron_energy_vector'+tag,positron_energy_vector)
#np.save('analysis/positron_energy_gap_vector'+tag,positron_energy_gap_vector)
#np.save('analysis/positron_true_dir_vector'+tag,positron_true_dir_vector)
#np.save('analysis/positron_rec_dir_vector'+tag,positron_rec_dir_vector)
#np.save('analysis/capture_time_vec'+tag,capture_time_vec)
#np.save('analysis/neutron_rec_dir_vector'+tag,neutron_rec_dir_vector)
#np.save('analysis/neutron_true_dir_vector'+tag,neutron_true_dir_vector)

print 'ananlysis data save in the analysis folder'
print 'The input file is ', inputfile, '. And the tag is ', tag



#out.Write()
#
#c = ROOT.TCanvas("c","c",800,600)
#c.Draw()
#hncos.Draw()
#c.Update()
#raw_input()
#
#c2 = ROOT.TCanvas("c","c",800,600)
#c2.Draw()
#hpcos.Draw()
#c2.Update()
#raw_input()
