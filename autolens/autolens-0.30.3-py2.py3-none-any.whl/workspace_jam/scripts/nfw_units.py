from autolens.model.profiles import mass_profiles as mp
from astropy import cosmology as cosmo

cosmology = cosmo.Planck15
redshift_lens = 0.6
redshift_source = 2.5

nfw = mp.SphericalNFW(kappa_s=0.1, scale_radius=1.0)

mass_at_200 = nfw.mass_at_200_for_units(
    unit_mass="solMass",
    unit_length="arcsec",
    redshift_profile=redshift_lens,
    redshift_source=redshift_source,
    cosmology=cosmology,
)

print(mass_at_200)

radius_at_200 = nfw.radius_at_200_for_units(
    unit_mass="solMass",
    unit_length="arcsec",
    redshift_profile=redshift_lens,
    redshift_source=redshift_source,
    cosmology=cosmology,
)

print(radius_at_200)

concentration = nfw.concentration_for_units(
    unit_mass="solMass",
    unit_length="arcsec",
    redshift_profile=redshift_lens,
    redshift_source=redshift_source,
    cosmology=cosmology,
)

print(concentration)

nfw = mp.SphericalTruncatedNFW(kappa_s=0.1, scale_radius=1.0, truncation_radius=1.0)

mass_at_truncation_radius = nfw.mass_at_truncation_radius(
    unit_mass="solMass",
    unit_length="arcsec",
    redshift_profile=redshift_lens,
    redshift_source=redshift_source,
    cosmology=cosmology,
)

print(mass_at_truncation_radius)
