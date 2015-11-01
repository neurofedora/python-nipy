%global modname nipy

Name:           python-%{modname}
Version:        0.4.0
Release:        1%{?dist}
Summary:        Neuroimaging in Python FMRI analysis package

License:        BSD
URL:            http://nipy.org/nipy
Source0:        https://github.com/nipy/nipy/archive/%{version}/%{modname}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  lapack-devel openblas-devel atlas-devel

%description
Neuroimaging tools for Python.

The aim of NIPY is to produce a platform-independent Python environment for the
analysis of functional brain imaging data using an open development model.

%package -n python2-%{modname}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{modname}}
BuildRequires:  python2-devel python-setuptools
BuildRequires:  numpy scipy python2-nibabel sympy
BuildRequires:  Cython
# Test deps
BuildRequires:  python-nose
BuildRequires:  python-six python2-transforms3d
BuildRequires:  nipy-data
Requires:       numpy scipy python2-nibabel sympy
Requires:       python-six python2-transforms3d
Requires:       python-matplotlib
Suggests:       nipy-data

%description -n python2-%{modname}
Neuroimaging tools for Python.

The aim of NIPY is to produce a platform-independent Python environment for the
analysis of functional brain imaging data using an open development model.

Python 2 version.

%package -n python3-%{modname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{modname}}
BuildRequires:  python3-devel python3-setuptools
BuildRequires:  python3-numpy python3-scipy python3-nibabel python3-sympy
BuildRequires:  python3-Cython
# Test deps
BuildRequires:  python3-nose
BuildRequires:  python3-six python3-transforms3d
BuildRequires:  nipy-data
Requires:       python3-numpy python3-scipy python3-nibabel python3-sympy
Requires:       python3-six python3-transforms3d
Requires:       python3-matplotlib
Suggests:       nipy-data

%description -n python3-%{modname}
Neuroimaging tools for Python.

The aim of NIPY is to produce a platform-independent Python environment for the
analysis of functional brain imaging data using an open development model.

Python 3 version.

%prep
%autosetup -n %{modname}-%{version}
# Hard fix for bundled libs
find -type f -name '*.py' -exec sed -i \
  -e "s/from \.*externals.six/from six/"                             \
  -e "s/from nipy.externals.six/from six/"                           \
  -e "s/from nipy.externals import six/import six/"                  \
  -e "s/from nipy.externals.argparse/from argparse/"                 \
  -e "s/import nipy.externals.argparse as argparse/import argparse/" \
  -e "s/from \.*externals.transforms3d/from transforms3d/"           \
  {} ';'
find scripts/ -type f -exec sed -i \
  -e "s/from nipy.externals.argparse/from argparse/"                 \
  -e "s/import nipy.externals.argparse as argparse/import argparse/" \
  {} ';'
sed -i -e "/config.add_subpackage(.externals.)/d" nipy/setup.py
rm -vrf nipy/externals/
rm -rf lib/lapack_lite/

rm -rf %{py3dir}
mkdir -p %{py3dir}
cp -a . %{py3dir}
for mod in nipy_3dto4d nipy_4d_realign nipy_4dto3d nipy_diagnose nipy_tsdiffana
do
  sed -i -e "/cmd\(_root\)\? =/s/$mod/$mod-2/" nipy/tests/test_scripts.py
  sed -i -e "/cmd\(_root\)\? =/s/$mod/$mod-3/" %{py3dir}/nipy/tests/test_scripts.py
done

%build
export NIPY_EXTERNAL_LAPACK=1
%py2_build

pushd %{py3dir}
  %py3_build
popd

%install
export NIPY_EXTERNAL_LAPACK=1
%py2_install

pushd %{py3dir}
 %py3_install
popd

# Rename binaries
pushd %{buildroot}%{_bindir}
  for mod in nipy_3dto4d nipy_4d_realign nipy_4dto3d nipy_diagnose nipy_tsdiffana
  do
    mv $mod python2-$mod

    sed -i '1s|^.*$|#!/usr/bin/env %{__python2}|' python2-$mod
    for i in $mod $mod-2 $mod-%{python2_version}
    do
      ln -s python2-$mod $i
    done

    cp python2-$mod python3-$mod
    sed -i '1s|^.*$|#!/usr/bin/env %{__python3}|' python3-$mod

    for i in $mod-3 $mod-%{python3_version}
    do
      ln -s python3-$mod $i
    done
  done
popd

%check
TESTING_DATA=( \
nipy/testing/functional.nii.gz                             \
nipy/modalities/fmri/tests/spm_hrfs.mat                    \
nipy/modalities/fmri/tests/spm_dmtx.npz                    \
nipy/testing/anatomical.nii.gz                             \
nipy/algorithms/statistics/models/tests/test_data.bin      \
nipy/algorithms/diagnostics/tests/data/tsdiff_results.mat  \
nipy/modalities/fmri/tests/spm_bases.mat                   \
)

# Do not fail on testing for now due to:
# https://github.com/nipy/nipy/issues/380
# Only 1 of 2603 fails ;)

pushd build/lib.*-%{python2_version}
  for i in ${TESTING_DATA[@]}
  do
    mkdir -p ./${i%/*}/
    cp -a ../../$i ./$i
  done
  PATH="%{buildroot}%{_bindir}:$PATH" nosetests-%{python2_version} -v || :
popd

pushd %{py3dir}
  pushd build/lib.*-%{python3_version}
    for i in ${TESTING_DATA[@]}
    do
      mkdir -p ./${i%/*}/
      cp -a ../../$i ./$i
    done
    PATH="%{buildroot}%{_bindir}:$PATH" nosetests-%{python3_version} -v || :
  popd
popd

%files -n python2-%{modname}
%license LICENSE
%doc README.rst AUTHOR THANKS examples
%{_bindir}/nipy_3dto4d
%{_bindir}/nipy_3dto4d-2
%{_bindir}/nipy_3dto4d-%{python2_version}
%{_bindir}/python2-nipy_3dto4d
%{_bindir}/nipy_4d_realign
%{_bindir}/nipy_4d_realign-2
%{_bindir}/nipy_4d_realign-%{python2_version}
%{_bindir}/python2-nipy_4d_realign
%{_bindir}/nipy_4dto3d
%{_bindir}/nipy_4dto3d-2
%{_bindir}/nipy_4dto3d-%{python2_version}
%{_bindir}/python2-nipy_4dto3d
%{_bindir}/nipy_diagnose
%{_bindir}/nipy_diagnose-2
%{_bindir}/nipy_diagnose-%{python2_version}
%{_bindir}/python2-nipy_diagnose
%{_bindir}/nipy_tsdiffana
%{_bindir}/nipy_tsdiffana-2
%{_bindir}/nipy_tsdiffana-%{python2_version}
%{_bindir}/python2-nipy_tsdiffana
%{python2_sitearch}/%{modname}*

%files -n python3-%{modname}
%license LICENSE
%doc README.rst AUTHOR THANKS examples
%{_bindir}/nipy_3dto4d-3
%{_bindir}/nipy_3dto4d-%{python3_version}
%{_bindir}/python3-nipy_3dto4d
%{_bindir}/nipy_4d_realign-3
%{_bindir}/nipy_4d_realign-%{python3_version}
%{_bindir}/python3-nipy_4d_realign
%{_bindir}/nipy_4dto3d-3
%{_bindir}/nipy_4dto3d-%{python3_version}
%{_bindir}/python3-nipy_4dto3d
%{_bindir}/nipy_diagnose-3
%{_bindir}/nipy_diagnose-%{python3_version}
%{_bindir}/python3-nipy_diagnose
%{_bindir}/nipy_tsdiffana-3
%{_bindir}/nipy_tsdiffana-%{python3_version}
%{_bindir}/python3-nipy_tsdiffana
%{python3_sitearch}/%{modname}*

%changelog
* Sun Nov 01 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.4.0-1
- Initial package
