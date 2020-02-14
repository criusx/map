# MAP - Modeling Architectural Platform
This is a framework designed and built by expert modeling/simulation engineers in the industry.  It's purpose is to provide a set of classes, tools, and flows to aid in modeling/simulation of complex hardware for the purpose of performance analysis and better hardware designs.

These classes and tools are also designed to work with existing platforms like Gem5 and SystemC while providing more abstract and flexible methodologies for quick analysis and study.

MAP is broken into two parts:
1. **Sparta** -- A set of C++ classes (C++17) used to construct, bind, and run full simulation designs and produce performance analysis data in text form, database form, or HDF5
1. **Helios** -- A set of python tools used to visualize, analyze, and deep dive data generated for a Sparta-built simulator

# MacOS building/running instructions

- Need python3
- Need PyYAML : https://pypi.org/simple/pyyaml/
-- Download PyYAML-5.3.tar.gz and untar
-- Run python3 steup.py install
- Install wx: brew install wxmac
- Install wxPython: python3 -mpip install wxpython
- Install matplotlib: python3 -mpip install matplotlib
- Install Cython: python3 -mpip install Cython
