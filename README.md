# Terrestrial Carbon Community Assimilation System (TCCAS) training 

<img src="https://github.com/soonyenju/tccas/blob/main/data/D%2BB_schematic.png" width="800"/>

The Terrestrial Carbon Community Assimilation System (TCCAS) is built around the coupled D&B terrestrial biosphere model. D&B has been newly developed based on the well-established DALEC and BETHY models and builds on the strengths of each component model. In particular, D&B combines the dynamic simulation of the carbon pools and canopy phenology of DALEC with the dynamic simulation of water pools, and the canopy model of photosynthesis and energy balance of BETHY. D&B includes a set of observation operators for optical as well as active and passive microwave observations. The focus of TCCAS is the combination of this diverse array of observational data streams with the D&B model into a consistent picture of the terrestrial carbon, water, and energy cycles. TCCAS applies a variational assimilation approach that adjusts a combination of initial pool sizes and process parameters to match the observational data streams.


TCCAS offers:
- Open source community model
- Observation operators for optical as well as active and passive microwave observations
- Tangent and adjoint codes
- Modular setup
- Computational efficiency
- Tested on point to regional scales
- Experienced developer team
- Documentation
- User support and Training

See TCCAS [website](https://tccas.inversion-lab.com/) and [user tutorial](https://tccas.inversion-lab.com/documentation/TCCAS_manual.pdf).

The hands-on sessions are delivered on the [PolarTep](https://tccas.hub.eox.at/) Jupyter Notebook platform.

For registered users, here is how to get the notebooks and slides.

```
%%bash
# # Copy shared/tccas/notebooks/ to home

cd ~
rm -r notebooks
cp -r /shared/tccas/notebooks/ ~
```

You can also run the notebooks on [Google Colab](https://colab.research.google.com/notebooks/intro.ipynb)

# Past Training Schools

- September 2025, Hamburg, Germany
- August 2025, Nanjing, China
- June 2025, Vienna, Austria
- October 2024, Frascati, Italy
- June 2025, online
- March 2024 Edinburgh, UK
