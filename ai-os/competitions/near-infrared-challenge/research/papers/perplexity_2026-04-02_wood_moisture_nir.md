# Perplexity Summary 2026-04-02: Wood Moisture NIR

## Source

- Origin: User-provided Perplexity research summary
- Saved on: 2026-04-02
- Scope: wood moisture NIR regression, species shift, preprocessing, wavelength selection

## Most Important Takeaways

- `PLS / PLSR` should remain the reference model family.
- `GroupKFold(species)` is essential, and `Leave-One-Species-Out` is strongly recommended as a diagnostic.
- `SNV`, `MSC`, `Savitzky-Golay derivatives`, and `detrending` are the main preprocessing families worth systematic comparison.
- `VIP`, `CARS`, `iPLS`, `siPLS`, `biPLS`, and related wavelength-selection methods are strong candidates for 1555-wave spectra.
- Public LB and CV mismatch is normal in NIR tasks, so fold variance matters.
- Small ensembles across preprocessing/model variants are likely useful.

## Suggested Papers And Themes

### Wood moisture / woody biomass

- Review of NIR for monitoring moisture and density of solid wood
- Accuracy of predicting wood moisture for multiple wood section types
- NIR and resistance-based moisture determination for logging residues and sweet sorghum
- Moisture prediction in soil-mixed woody biomass with `SNV + SG + PLSR`
- Effect of specimen thickness and moisture range on wood moisture predictability

### Preprocessing / wavelength selection

- Combined optimization of `Savitzky-Golay` and `MSC`
- Graphical evaluation of preprocessing in multivariate regression
- Comparison of NIR preprocessing methods including `SNV`, `MSC`, `detrending`, `SG derivative`
- Joint optimization of preprocessing, latent variables, and `VIP`
- Reviews and evaluations of `iPLS`, `siPLS`, `biPLS`, `CARS`, `UVE`, `VIP`

## Transfer To This Project

- The current project direction already aligns with the literature: `PLS + careful preprocessing + wavelength selection`.
- The strongest missing pieces are `MSC`, more systematic `SG` parameter search, and stronger wavelength selection than plain correlation ranking.
- Evaluation should explicitly separate "best CV model" from "best unknown-species model".

## URLs Mentioned In The Perplexity Summary

- https://cir.nii.ac.jp/crid/1364233270908169472
- https://bioresources.cnr.ncsu.edu/resources/accuracy-of-predicting-the-moisture-content-of-three-types-of-wood-sections-using-near-infrared-spectroscopy/
- https://bioresources.cnr.ncsu.edu/resources/investigation-of-nir-spectroscopy-and-electrical-resistance-based-approaches-for-moisture-determination-of-logging-residues-and-sweet-sorghum/
- https://www.nature.com/articles/s41598-026-36901-8
- https://scienceacademique.com/archives/2321
- https://onlinelibrary.wiley.com/doi/10.1155/2013/642190
- https://pubmed.ncbi.nlm.nih.gov/20132601/
- https://www.sciencedirect.com/science/article/abs/pii/S0003267021010813
- https://www.nature.com/articles/srep11647
- https://journals.sagepub.com/doi/abs/10.1177/09670335221097236
- https://www.sciencedirect.com/science/article/abs/pii/S0169743909001841
- https://www.sciencedirect.com/science/article/abs/pii/S0169743919302643
- http://libpls.net/publication/CARS_2009.pdf

## Candidate Experiments Added By This Summary

- `MSC + SG + PLS`
- `Detrending + PLS`
- `VIP + PLS`
- `CARS + PLS`
- `iPLS family + PLS`
- `Elastic Net` baseline track
- `Leave-One-Species-Out` diagnostic track
- Small preprocessing/model ensemble
