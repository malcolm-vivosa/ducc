# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright(C) 2019-2020 Max-Planck-Society

from time import time

import ducc0.wgridder.experimental as wgridder
import ducc0
import matplotlib.pyplot as plt
import numpy as np


def get_npixdirty(uvw, freq, fov_deg, mask):
    speedOfLight = 299792458.
    bl = np.sqrt(uvw[:,0]**2+uvw[:,1]**2+uvw[:,2]**2)
    bluvw = bl.reshape((-1,1))*freq.reshape((1,-1))/speedOfLight
    maxbluvw = np.max(bluvw*mask)
    minsize = int((2*fov_deg*np.pi/180*maxbluvw)) + 1
    return minsize+(minsize%2)  # make even


def main():
#    ms, fov_deg = '/home/martin/ms/supernovashell.55.7+3.4.spw0.npz', 2.
#    ms, fov_deg = '/home/martin/ms/1052736496-averaged.npz', 25.
#    ms, fov_deg = '/home/martin/ms/1052735056.npz', 45.
#    ms, fov_deg = '/home/martin/ms/G330.89-0.36.npz', 2.
#    ms, fov_deg = '/home/martin/ms/bigms.npz', 0.0005556*1800
#    ms, fov_deg = '/home/martin/ms/L_UV_DATA-IF1.npz', 1.
    ms, fov_deg = '/data/CYG-ALL-13360-8MHZ.npz', 1.
    ms, fov_deg = '/data/L_UV_DATA-IF1.npz', 1.

    data = np.load(ms)
    uvw, freq, vis, wgt = data["uvw"], data["freqs"], data["vis"], data["wgt"]
    mask = data["mask"] if "mask" in data else None

    wgt[vis == 0] = 0
    if mask is None:
        mask = np.ones(wgt.shape, dtype=np.uint8)
    mask[wgt == 0] = False
    DEG2RAD = np.pi/180
    nthreads = 8
    epsilon = 1e-4
    do_wgridding = False

    ntries_gpu = 1

    npixdirty = get_npixdirty(uvw, freq, fov_deg, mask)
    pixsize = fov_deg/npixdirty*DEG2RAD

    print('Start gridding...')
    t0 = time()
    dirty = wgridder.vis2dirty(
        uvw=uvw, freq=freq, vis=vis, wgt=wgt,
        mask=mask, npix_x=npixdirty, npix_y=npixdirty, pixsize_x=pixsize,
        pixsize_y=pixsize, epsilon=epsilon, do_wgridding=do_wgridding,
        nthreads=nthreads, verbosity=1, flip_v=True, gpu=False)
    t = time() - t0
    print("{} s".format(t))
    print("{} visibilities/thread/s".format(np.sum(wgt != 0)/nthreads/t))
    t0 = time()
    dirty_g = wgridder.vis2dirty(
        uvw=uvw, freq=freq, vis=vis, wgt=wgt,
        mask=mask, npix_x=npixdirty, npix_y=npixdirty, pixsize_x=pixsize,
        pixsize_y=pixsize, epsilon=epsilon, do_wgridding=do_wgridding,
        nthreads=nthreads, verbosity=1, flip_v=True, gpu=True)
    t = time() - t0
    print("{} s".format(t))
    print("{} visibilities/thread/s".format(np.sum(wgt != 0)/nthreads/t))
    print(ducc0.misc.l2error(dirty,dirty_g))
    fig, axs = plt.subplots(1,3)
    axs[0].imshow(dirty.T, origin='lower')
    axs[1].imshow(dirty_g.T, origin='lower')
    axs[2].imshow(np.minimum(10.,np.maximum(-10.,dirty_g.T/dirty.T)), origin='lower')
    plt.show()
    t0 = time()
    x0 = wgridder.dirty2vis(
        uvw=uvw, freq=freq, dirty=dirty, wgt=wgt,
        mask=mask, pixsize_x=pixsize, pixsize_y=pixsize, epsilon=epsilon,
        do_wgridding=do_wgridding, nthreads=nthreads, verbosity=1,
        flip_v=True)
    t = time() - t0
    print("{} s".format(t))
    print("{} visibilities/thread/s".format(np.sum(wgt != 0)/nthreads/t))

    t0 = time()
    for _ in range(ntries_gpu):
        x1 = wgridder.dirty2vis(
            uvw=uvw, freq=freq, dirty=dirty, wgt=wgt,
            mask=mask, pixsize_x=pixsize, pixsize_y=pixsize, epsilon=epsilon,
            do_wgridding=do_wgridding,
            nthreads=nthreads, verbosity=1,
            flip_v=True,
            gpu=True)
    t = (time() - t0)/ntries_gpu
    print("{} s".format(t))
    print("{} visibilities/thread/s".format(np.sum(wgt != 0)/nthreads/t))
    print(ducc0.misc.l2error(x0,x1))
    plt.imshow(dirty.T, origin='lower')
    plt.show()


if __name__ == "__main__":
    main()
