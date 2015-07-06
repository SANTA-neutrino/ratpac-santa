import sys, os
import numpy as np
import scipy
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, pickle

#tag for data storage
if len(sys.argv)>=2:
    tag = sys.argv[1]
else:
    tag = 'test'

print 'the tag is ', tag



#folder names
bens_computer = True
work_computer = False
cynthias_computer = False
# if bens_computer == True:
#     santa_dir= '/Users/bsafdi/Code/SANTA/github/ratpac-santa/analysis/'
if cynthias_computer == True:
    santa_dir= '/Users/cynthiagerlein/Dropbox (Personal)/ben/santa/analysis/'
elif work_computer == True or bens_computer == True:
    santa_dir = '/Users/bsafdi/Dropbox/santa/analysis/'
    data_dir = santa_dir + 'data/'
data_dir_tag = data_dir + tag + '/'
plots_dir = santa_dir + 'plots/'
plots_dir_tag = plots_dir + tag + '/'

#make dirs
dirs = [data_dir,data_dir_tag,plots_dir, plots_dir_tag]

def make_dirs():
    for d in dirs:
        print 'one the dir ', d
        if not os.path.exists(d):
            os.mkdir(d)

make_dirs()

#==============================
#global constants
Delta = 1.29 #MeV
Mn = 939 #MeV
me = 0.511 #MeV

#==============================
#analysis cuts
#input variables
t_min = 1 #ns
t_max = 10000 #ns
cos_theta_en_cut = 0 #only keep events with cos_theta_en less than this
pos_energy_ratio_cut = 0

#==============================
#define some global functions for reconstructing the positron's direction
def return_Enu(Eep):
    return Eep + Delta + me

def return_Kn(Eep,cos_theta_en):
    cos_2_theta = 2*(cos_theta_en**2)-1
    sin_squared_theta = 1 - cos_theta_en**2
    
    Enu = return_Enu(Eep) #antineutrino's energy
    pe = np.sqrt((Eep+me)**2 - me**2)

    Kn = Enu**2 / (2*Mn) + ((pe**2) / (2*Mn))*(cos_2_theta - 2*cos_theta_en*np.sqrt((Enu/pe)**2 - sin_squared_theta))

    return Kn

def cos_vectors(a,b):
    return np.dot(a,b) / np.sqrt(np.dot(a,a)*np.dot(b,b))


def return_pnu(Eep,pn,pe):
    cos_theta_en = cos_vectors(pn,pe)
    Kn = return_Kn(Eep,cos_theta_en)

    pn = np.sqrt(2*Mn*Kn)*pn

    return pn + np.sqrt((Eep+me)**2 - me**2)*pe/np.dot(pe,pe) #assuming Eep is positron's kinetic energy

#==============================
#define some global functions for plotting
def make_icdf(prob_hist):
    icdf_hist = np.array([np.sum( prob for prob in prob_hist[i:-1] ) for i in range(np.size(prob_hist)) ])
    return icdf_hist

#==============================
#Load the files
file_positron_energy_vector = open(data_dir_tag + 'positron_energy_vector-'+tag+'.json')
file_positron_energy_gap_vector = open(data_dir_tag + 'positron_energy_gap_vector-'+tag+'.json')
file_positron_true_dir_vector = open(data_dir_tag + 'positron_true_dir_vector-'+tag+'.json')
file_positron_rec_dir_vector = open(data_dir_tag + 'positron_rec_dir_vector-'+tag+'.json')
file_capture_time_vec = open(data_dir_tag + 'capture_time_vec-'+tag+'.json')
file_neutron_rec_dir_vector = open(data_dir_tag + 'neutron_rec_dir_vector-'+tag+'.json')
file_neutron_true_dir_vector = open(data_dir_tag + 'neutron_true_dir_vector-'+tag+'.json')
file_ibd_pos_vector = open(data_dir_tag + 'ibd_pos_vector-'+tag+'.json')

positron_energy_vector = np.array(pickle.load(file_positron_energy_vector))
positron_energy_gap_vector = np.array(pickle.load(file_positron_energy_gap_vector))
positron_true_dir_vector = np.array(pickle.load( file_positron_true_dir_vector))
positron_rec_dir_vector = np.array(pickle.load(file_positron_rec_dir_vector))
capture_time_vec = np.array(pickle.load(file_capture_time_vec))
neutron_rec_dir_vector = np.array(pickle.load(file_neutron_rec_dir_vector))
neutron_true_dir_vector = np.array(pickle.load(file_neutron_true_dir_vector))
ibd_pos_vector = np.array(pickle.load(file_ibd_pos_vector))

#==============================
#do the analysis

num_events = np.size(capture_time_vec)

positron_bool = np.array(positron_energy_gap_vector,np.dtype('bool'))
neutron_bool = np.array(capture_time_vec,np.dtype('bool'))

total_events_bool = positron_bool*neutron_bool

cos_nu_rec_vec = []
cos_nu_rec_vec_true_p = []
cos_nu_rec_vec_true = []
cos_nu_rec_vec_n_only = []
ibd_dist_vec = []
timing_vec = []

cos_n_from_true = []
cos_p_from_true = []

nevents = 0
for i in range(num_events):
    print 'The capture time is ', capture_time_vec[i]
    if capture_time_vec[i]> 0:
        timing_vec.append(capture_time_vec[i])
    if total_events_bool[i] and capture_time_vec[i] > t_min and capture_time_vec[i] < t_max and positron_energy_gap_vector[i] / positron_energy_vector[i] > pos_energy_ratio_cut:
#    and positron_energy_vector[i] + me < 2:
        cos_en = cos_vectors(positron_rec_dir_vector[i],neutron_rec_dir_vector[i])
        if cos_en < cos_theta_en_cut: # and neutron_rec_dir_vector[i][2] > 0: # cos_theta_en_cut: # and cos_vectors(neutron_rec_dir_vector[i],neutron_true_dir_vector[i]) >0.9999:
            nevents = nevents+1
            pnu = return_pnu(positron_energy_vector[i],neutron_rec_dir_vector[i],positron_rec_dir_vector[i])
            pnu_true_p = return_pnu(positron_energy_vector[i],neutron_rec_dir_vector[i],positron_true_dir_vector[i])
            pnu_true = return_pnu(positron_energy_vector[i],neutron_true_dir_vector[i],positron_true_dir_vector[i])
            
            
            
            cos_nu_rec_vec.append(cos_vectors(pnu,[0,0,1]))
            cos_nu_rec_vec_true_p.append(cos_vectors(pnu_true_p,[0,0,1]))
            cos_nu_rec_vec_true.append(cos_vectors(pnu_true,[0,0,1]))
            cos_nu_rec_vec_n_only.append(cos_vectors(neutron_rec_dir_vector[i],[0,0,1]))
            ibd_dist_vec.append(np.sqrt(np.dot(np.array(ibd_pos_vector[i]),np.array(ibd_pos_vector[i])))/10)

            cos_n_from_true.append(cos_vectors(neutron_rec_dir_vector[i],neutron_true_dir_vector[i]))
            cos_p_from_true.append(cos_vectors(positron_rec_dir_vector[i],positron_true_dir_vector[i]))

capture_time_hist, capture_time_hist_values = np.histogram(timing_vec, bins=50,range=(0,10000))
ibd_dist_hist, hist_dist_vals_long = np.histogram(ibd_dist_vec, bins=100, range=(0,200) )
hist_dist_vals = [ (hist_dist_vals_long[i] + hist_dist_vals_long[i+1] )/ 2 for i in range(np.size(hist_dist_vals_long)-1)]

theta_nu_rec_hist, theta_vals_long = np.histogram(np.arccos(np.array(cos_nu_rec_vec)), bins=1000, range=(0,np.pi))
theta_nu_rec_hist_true_p = np.histogram(np.arccos(cos_nu_rec_vec_true_p), bins=1000, range=(0,np.pi))[0]
theta_nu_rec_hist_true = np.histogram(np.arccos(cos_nu_rec_vec_true), bins=1000, range=(0,np.pi))[0]
theta_nu_rec_hist_n_only = np.histogram(np.arccos(cos_nu_rec_vec_n_only), bins=1000, range=(0,np.pi))[0]
theta_n_rec_hist = np.histogram(np.arccos(cos_n_from_true), bins=1000, range=(0,np.pi))[0]
theta_p_rec_hist = np.histogram(np.arccos(cos_p_from_true), bins=1000, range=(0,np.pi))[0]

#print cos_n_from_true

theta_nu_rec_hist_norm = theta_nu_rec_hist / np.float(np.sum(theta_nu_rec_hist))
theta_nu_rec_hist_true_p_norm = theta_nu_rec_hist_true_p / np.float(np.sum(theta_nu_rec_hist_true_p))
theta_nu_rec_hist_n_only_norm = theta_nu_rec_hist_n_only / np.float(np.sum(theta_nu_rec_hist_n_only))
theta_n_rec_hist_norm = theta_n_rec_hist / np.float(np.sum(theta_n_rec_hist))
theta_p_rec_hist_norm = theta_p_rec_hist / np.float(np.sum(theta_p_rec_hist))


theta_nu_icdf_hist = make_icdf(theta_nu_rec_hist_norm)
theta_nu_icdf_hist_true_p = make_icdf(theta_nu_rec_hist_true_p_norm)
theta_nu_icdf_hist_n_only = make_icdf(theta_nu_rec_hist_n_only_norm)
theta_n_icdf_hist = make_icdf(theta_n_rec_hist_norm)
theta_p_icdf_hist = make_icdf(theta_p_rec_hist_norm)

np.save(plots_dir_tag+'theta_nu_icdf_hist',theta_nu_icdf_hist)
np.save(plots_dir_tag+'theta_nu_icdf_hist_true_p',theta_nu_icdf_hist_true_p)
np.save(plots_dir_tag+'theta_nu_icdf_hist_n_only',theta_nu_icdf_hist_n_only)

theta_vals = [(360/(2*np.pi))*(theta_vals_long[i]+theta_vals_long[i+1])/2. for i in range(np.size(theta_vals_long)-1)]
#theta_vals = np.arccos(np.array(theta_vals))

np.save(plots_dir_tag+'theta_vals',theta_vals)


print 'The fraction of events that made it through was ', np.float(nevents) / num_events

#==============================
#plot results
plt.figure(figsize=(8,6))
plt.plot(theta_vals,theta_nu_rec_hist, drawstyle='steps-mid', label='all rec.')
plt.plot(theta_vals,theta_nu_rec_hist_true_p, drawstyle='steps-mid', label='exact e+')
plt.plot(theta_vals,theta_nu_rec_hist_true, drawstyle='steps-mid', label='exact e+ and n')
plt.plot(theta_vals,theta_nu_rec_hist_n_only, drawstyle='steps-mid', label='n only')
plt.legend(fontsize=14)
plt.savefig(plots_dir_tag + 'rec_nubar_dir.pdf')
plt.close()

plt.figure(figsize=(8,6))
plt.plot(theta_vals,theta_nu_icdf_hist, drawstyle='steps-mid', label='all rec.')
plt.plot(theta_vals,theta_nu_icdf_hist_true_p, drawstyle='steps-mid', label='exact e+')
plt.plot(theta_vals,theta_nu_icdf_hist_n_only, drawstyle='steps-mid', label='n only')
plt.legend(fontsize=14)
plt.xlabel('reconstructed angle [degrees]', fontsize=18)
plt.ylabel('inverse cumulative probability', fontsize=18)
plt.tick_params(axis='x', length=5,width=2,labelsize=18)
plt.tick_params(axis='y',length=5,width=2,labelsize=18)
plt.title('Antineutrino angular resolution',fontsize=18)
plt.savefig(plots_dir_tag + 'icdf.pdf')
plt.close()

plt.figure(figsize=(8,6))
plt.plot(theta_vals,theta_n_icdf_hist, drawstyle='steps-mid', label='recon. n dir.')
plt.plot(theta_vals,theta_p_icdf_hist, drawstyle='steps-mid', label='recon. pos. dir.')
plt.legend(fontsize=14)
plt.savefig(plots_dir_tag + 'neutron_dir.pdf')
plt.close()


plt.figure(figsize=(8,6))
plt.plot(capture_time_hist_values[0:-1],capture_time_hist, drawstyle='steps-mid')
#plt.legend(fontsize=14)
plt.xlabel('capture time [ns]', fontsize=18)
plt.ylabel('events', fontsize=18)
plt.tick_params(axis='x', length=5,width=2,labelsize=18)
plt.tick_params(axis='y',length=5,width=2,labelsize=18)
plt.title('Neutron capture time',fontsize=18)
plt.savefig(plots_dir_tag + 'capture_time.pdf')
plt.close()

plt.figure(figsize=(8,6))
plt.plot(hist_dist_vals,ibd_dist_hist, drawstyle='steps-mid', label='IBD dist. from center')
plt.legend(fontsize=14)
plt.savefig(plots_dir_tag + 'IBD_dist.pdf')
plt.close()



#print 'the mean reconstructed theta  for recon. e+, exact e+, and n only are ', np.mean(theta_nu_rec_vec), np.mean(theta_nu_rec_vec_true_p), np.mean(theta_nu_rec_vec_n_only)
#
#print 'the median reconstructed theta for recon. e+, exact e+, and n only are ', np.median(cos_nu_rec_vec), np.median(theta_nu_rec_vec_true_p), np.median(theta_nu_rec_vec_n_only)




#print positron_energy_vector





