/*
 *  This file is part of libsharp2.
 *
 *  libsharp2 is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  libsharp2 is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with libsharp2; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* libsharp2 is being developed at the Max-Planck-Institut fuer Astrophysik */

/*! \file sharp_almhelpers.h
 *  SHARP helper function for the creation of a_lm data structures
 *
 *  Copyright (C) 2008-2019 Max-Planck-Society
 *  \author Martin Reinecke
 */

#ifndef SHARP2_ALMHELPERS_H
#define SHARP2_ALMHELPERS_H


#include <memory>
#include "libsharp2/sharp.h"

/*! \internal
    Helper type for index calculation in a_lm arrays. */
class sharp_standard_alm_info: public sharp_alm_info
  {
  private:
    /*! Maximum \a l index of the array */
    size_t lmax_;
    /*! Array with \a nm entries containing the individual m values */
    std::vector<size_t> mval_;
    /*! Array with \a nm entries containing the (hypothetical) indices of
        the coefficients with quantum numbers 0,\a mval[i] */
    std::vector<ptrdiff_t> mvstart;
    /*! Stride between a_lm and a_(l+1),m */
    ptrdiff_t stride;

  public:
  /*! Creates an a_lm data structure from the following parameters:
      \param lmax maximum \a l quantum number (>=0)
      \param mmax maximum \a m quantum number (0<= \a mmax <= \a lmax)
      \param stride the stride between entries with identical \a m, and \a l
        differing by 1.
      \param mstart the index of the (hypothetical) coefficient with the
        quantum numbers 0,\a m. Must have \a mmax+1 entries.
   */
    sharp_standard_alm_info(size_t lmax__, size_t mmax_, ptrdiff_t stride_, const ptrdiff_t *mstart);

  /*! Creates an a_lm data structure which from the following parameters:
      \param lmax maximum \a l quantum number (\a >=0)
      \param nm number of different \a m (\a 0<=nm<=lmax+1)
      \param stride the stride between entries with identical \a m, and \a l
        differing by 1.
      \param mval array with \a nm entries containing the individual m values
      \param mvstart array with \a nm entries containing the (hypothetical)
        indices of the coefficients with the quantum numbers 0,\a mval[i]
   */
    sharp_standard_alm_info (size_t lmax__, size_t nm__, ptrdiff_t stride_, const size_t *mval__,
      const ptrdiff_t *mvstart_);
  /*! Returns the index of the coefficient with quantum numbers \a l,
      \a mval_[mi].
      \note for a \a sharp_alm_info generated by sharp_make_alm_info() this is
      the index for the coefficient with the quantum numbers \a l, \a mi. */
    ptrdiff_t index (int l, int mi);

    virtual ~sharp_standard_alm_info() {}
    virtual size_t lmax() const { return lmax_; }
    virtual size_t mmax() const;
    virtual size_t nm() const { return mval_.size(); }
    virtual size_t mval(size_t i) const { return mval_[i]; }
    virtual void clear_alm(std::complex<double> *alm) const;
    virtual void clear_alm(std::complex<float> *alm) const;
    virtual void get_alm(size_t mi, const std::complex<double> *alm, std::complex<double> *almtmp, size_t nalm) const;
    virtual void get_alm(size_t mi, const std::complex<float> *alm, std::complex<double> *almtmp, size_t nalm) const;
    virtual void add_alm(size_t mi, const std::complex<double> *almtmp, std::complex<double> *alm, size_t nalm) const;
    virtual void add_alm(size_t mi, const std::complex<double> *almtmp, std::complex<float> *alm, size_t nalm) const;
  };

/*! Initialises an a_lm data structure according to the scheme used by
    Healpix_cxx.
    \ingroup almgroup */
std::unique_ptr<sharp_standard_alm_info> sharp_make_triangular_alm_info (int lmax, int mmax, int stride);

/*! Initialises an a_lm data structure according to the scheme used by
    Fortran Healpix
    \ingroup almgroup */
std::unique_ptr<sharp_standard_alm_info> sharp_make_rectangular_alm_info (int lmax, int mmax, int stride);

#endif
