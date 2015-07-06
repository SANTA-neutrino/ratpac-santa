import sys, os
import numpy as np
import scipy
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, pickle

from numpy.random import random_sample

#tag for data storage
if len(sys.argv)>=2:
    tag = sys.argv[1]
else:
    tag = 'test'

print 'the tag is ', tag



#folder names
bens_computer = False
work_computer = True
cynthias_computer = False
if bens_computer == True:
    santa_dir= '/Users/bsafdi/Code/SANTA/github/ratpac-santa/analysis/'
elif cynthias_computer == True:
    santa_dir= '/Users/cynthiagerlein/Dropbox (Personal)/ben/santa/analysis/'
elif work_computer == True:
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

def weighted_values(values, probabilities, size):
            probabilities = probabilities/np.sum(probabilities)
            bins = np.add.accumulate(probabilities)
            return values[np.digitize(random_sample(size), bins)]

#==============================
#define some global functions for plotting
def make_icdf(prob_hist):
    icdf_hist = np.array([np.sum( prob for prob in prob_hist[i:-1] ) for i in range(np.size(prob_hist)) ])
    return icdf_hist

theta_nu_icdf_hist = np.load(plots_dir_tag+'theta_nu_icdf_hist.npy')
theta_nu_icdf_hist_true_p = np.load(plots_dir_tag+'theta_nu_icdf_hist_true_p.npy')
theta_nu_icdf_hist_n_only = np.load(plots_dir_tag+'theta_nu_icdf_hist_n_only.npy')
theta_nu_icdf_hist_mono = np.load('mono_y.npy')

# print theta_nu_icdf_hist_mono

theta_vals = np.load(plots_dir_tag+'theta_vals.npy')
theta_vals_mono = np.load('mono_x.npy')/2

theta_nu_icdf_hist_mono = theta_nu_icdf_hist_mono + 0.85*(np.cos(theta_vals_mono*1*np.pi/360))**2

#theta_nu_icdf_hist_mono = (np.cos(theta_vals_mono*1*np.pi/360))**2

def ICDF_to_PDF(icdf,theta):
    pdf = [-(icdf[i+1]-icdf[i])/(theta[i+1]-theta[i]) for i in range(np.size(theta)-1)]
    pdf = pdf +pdf[-1]
    return pdf

theta_nu_icdf_hist_mono = ICDF_to_PDF(theta_nu_icdf_hist_mono,theta_vals_mono)
theta_nu_icdf_hist_true_p = ICDF_to_PDF(theta_nu_icdf_hist_true_p,theta_vals)
theta_nu_icdf_hist_n_only = ICDF_to_PDF(theta_nu_icdf_hist_n_only,theta_vals)
theta_nu_icdf_hist = ICDF_to_PDF(theta_nu_icdf_hist,theta_vals)


theta_vals_mono = theta_vals_mono[0:-1]
theta_vals = theta_vals[0:-1]

plt.plot(theta_vals_mono,theta_nu_icdf_hist_mono)
plt.savefig(plots_dir_tag+'mono_pdf.pdf')
plt.close()

plt.plot(theta_vals,theta_nu_icdf_hist_n_only)
plt.savefig(plots_dir_tag+'n_only_pdf.pdf')
plt.close()

# print theta_nu_icdf_hist_n_only

# print theta_vals_mono

# print theta_vals

phi_vals = np.array([360*i/np.size(theta_vals) for i in range(np.size(theta_vals)) ])
phi_vals_mono = np.array([360*i/np.size(theta_vals_mono) for i in range(np.size(theta_vals_mono)) ])
phi_weights = np.ones(np.size(phi_vals))
phi_weights_mono = np.ones(np.size(phi_vals_mono))

#==============================
#generate randome points
ndays = 10
theta_MC = np.array(weighted_values(theta_vals,theta_nu_icdf_hist, 500*0.2*ndays))*2*np.pi/360
theta_MC_true_p = np.array(weighted_values(theta_vals,theta_nu_icdf_hist_true_p, 500*0.2*ndays))*2*np.pi/360
theta_MC_n_only= np.array(weighted_values(theta_vals,theta_nu_icdf_hist_n_only, 500*0.4*ndays))*2*np.pi/360
theta_MC_iso = np.array(weighted_values(theta_vals,phi_weights, 500*0.2*ndays))*2*np.pi/360
theta_MC_mono= np.array(weighted_values(theta_vals_mono,theta_nu_icdf_hist_mono, 500*0.4*ndays))*2*np.pi/360


phi_MC = np.array(weighted_values(phi_vals,phi_weights, 500*0.2*ndays))*2*np.pi/360
phi_MC_n_only = np.array(weighted_values(phi_vals,phi_weights, 500*0.4*ndays))*2*np.pi/360
phi_MC_mono = np.array(weighted_values(phi_vals_mono,phi_weights_mono, 500*0.4*ndays))*2*np.pi/360
# print theta_MC
# for i in range(np.size(theta_MC)):
#     if theta_MC[i] < np.pi/2:
#         print 'was ', theta_MC[i]
#         theta_MC[i] = theta_MC[i] + np.pi/2
#         print 'now ', theta_MC[i]
#     elif theta_MC[i] > np.pi/2:
#         theta_MC[i] = theta_MC[i] - np.pi/2


#==============================
#plot
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

import healpy as hp
import mpmath as mp
from astropy.io import fits

nside = 128/2**1
npix = hp.nside2npix(nside)

def return_masked_array(nside,theta_MC,phi_MC):
    pix_vector = hp.ang2pix(nside, theta_MC, phi_MC)
    fake_data = np.zeros(npix)
    for pix in pix_vector:
        fake_data[pix] = fake_data[pix]+1
    fake_data_masked = hp.ma(fake_data)
    fake_data_masked.mask = np.logical_not(fake_data)
    return fake_data_masked

def make_fake_data_iso():
    random_vector = np.random.random_integers(0,npix-1,np.size(phi_MC_n_only))
    fake_data = np.zeros(npix)
    for pix in random_vector:
        fake_data[pix] = fake_data[pix]+1
    fake_data_masked = hp.ma(fake_data)
    fake_data_masked.mask = np.logical_not(fake_data)
    return fake_data_masked

def return_masked_array_with_iso(nside,theta_MC,phi_MC,ratio = 1):
    random_vector = np.random.random_integers(0,npix-1,np.size(theta_MC)*ratio)
    pix_vector = hp.ang2pix(nside, theta_MC, phi_MC)
    pix_vector = np.concatenate((pix_vector,random_vector))
    fake_data = np.zeros(npix)
    for pix in pix_vector:
        fake_data[pix] = fake_data[pix]+1
    fake_data_masked = hp.ma(fake_data)
    fake_data_masked.mask = np.logical_not(fake_data)
    return fake_data_masked


fake_data_masked_iso = make_fake_data_iso()
fake_data_masked = return_masked_array(nside,theta_MC,phi_MC)
fake_data_masked_true_p = return_masked_array(nside,theta_MC_true_p,phi_MC)
fake_data_masked_n_only = return_masked_array(nside,theta_MC_n_only,phi_MC_n_only)

fake_data_masked_true_p_back = return_masked_array_with_iso(nside,theta_MC_true_p,phi_MC)
fake_data_masked_n_only_back = return_masked_array_with_iso(nside,theta_MC_n_only,phi_MC_n_only)

fake_data_masked_mono = return_masked_array(nside,theta_MC_mono,phi_MC_mono)

plt.hist(theta_MC_mono*360/(2*np.pi),100)
plt.savefig(plots_dir_tag+'mono_hist.pdf')
plt.close()


# hp.mollview(fake_data_masked,rot = (0,90),min=0,max=12)
# plt.savefig(plots_dir_tag+'fake_data.pdf')
# plt.close()
hp.mollview(fake_data_masked_mono,rot = (0,90),min=1,title = 'Monolithic detector')
plt.savefig(plots_dir_tag+'fake_data_masked_mono.pdf')
plt.close()

hp.mollview(fake_data_masked,rot = (0,90),min=1,title = 'Realistic')
plt.savefig(plots_dir_tag+'fake_data_masked.pdf')
plt.close()

hp.mollview(fake_data_masked_iso,rot = (0,90),min=1,title = 'Monolithic detector')
plt.savefig(plots_dir_tag+'fake_data_masked_iso.pdf')
plt.close()

hp.mollview(fake_data_masked_true_p,rot = (0,90),min=1,title = 'Neutron + positron')
plt.savefig(plots_dir_tag+'fake_data_masked_true_p.pdf')
plt.close()

hp.mollview(fake_data_masked_n_only,rot = (0,90),min=1,title = 'Neutron only')
plt.savefig(plots_dir_tag+'fake_data_masked_n_only.pdf')
plt.close()

hp.mollview(fake_data_masked_n_only_back,rot = (0,90),min=1,title = 'Neutron only + (1x) isotropic background')
plt.savefig(plots_dir_tag+'fake_data_masked_n_only_back.pdf')
plt.close()

hp.mollview(fake_data_masked_true_p_back,rot = (0,90),min=1,title = 'Neutron + positron + (1x) isotropic background')
plt.savefig(plots_dir_tag+'fake_data_masked_true_p_back.pdf')
plt.close()

