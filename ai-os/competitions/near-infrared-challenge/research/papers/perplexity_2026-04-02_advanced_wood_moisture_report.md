# Perplexity Summary 2026-04-02: Advanced Wood Moisture NIR Report

## Source

- Origin: User-provided Perplexity research summary
- Saved on: 2026-04-02
- Scope: advanced wood moisture prediction, species gap mitigation, validation strategy, domain adaptation

## Most Important Takeaways

- `PLSR` remains the central model family for this task shape: medium sample size, high-dimensional wavelengths, and strong multicollinearity.
- `GroupKFold(species)` is more trustworthy than plain `KFold`, and `Leave-One-Species-Out` / nested group validation should be emphasized.
- `Savitzky-Golay derivative + SNV/MSC/detrending` is strongly supported in the wood-moisture literature.
- `iPLS`, `CARS`, and `VIP` are safer wavelength-selection families than simple top-k correlation ranking.
- `EPO` and domain-adaptation ideas are promising, but they must target nuisance variation such as species/surface/batch, not the moisture signal itself.
- Robust ensembles of preprocessing-specific PLS models may be more reliable than a single nominally best model.

## Key Paper Themes

### Wood moisture / wood science reviews

- NIR for monitoring moisture content and density of solid wood
- Recent applications of NIR to wood science and technology
- Challenges in using NIR for improving wood quality
- Moisture-based sorting of green hem-fir timber
- Moisture prediction across wood sections
- Handheld NIR moisture determination in wood
- Portable NIR for industrial wood-chip moisture

### Domain adaptation and nuisance correction

- EPO for wood species identification under moisture variation
- EPO for removing moisture effects in soil Vis-NIR
- Domain-invariant PLS regression

## Transfer To This Project

- The next step should focus more on robust validation and PLS-consistent wavelength selection than on simple correlation ranking.
- `iPLS`, interval models, and harder validation schemes are especially well aligned with the current empirical results.
- `EPO` should be explored only as species/surface nuisance removal, not as direct moisture correction.
- Interval- and preprocessing-based ensembles deserve high priority.

## Practical Next Experiments Highlighted By This Summary

1. Nested LOSO-PLS preprocessing sweep
2. Replace correlation top-k with `iPLS`
3. Compare stable `CARS-PLS` vs `VIP-PLS`
4. Preprocessing ensemble of multiple PLS models
5. Two-layer `PLS + Ridge` ensemble
6. `Leave-Two-Species-Out` or hardest-fold-oriented model selection
7. Spectral-cluster local models
8. `di-PLS` trial with species as domains
9. Tail-focused models for extreme moisture ranges

## URLs Mentioned In The Summary

- https://pubs.cif-ifc.org/doi/pdf/10.5558/tfc2013-111
- https://link.springer.com/content/pdf/10.1007/s10086-015-1467-x.pdf
- https://jyx.jyu.fi/bitstreams/07f958a1-3bbc-42d5-9487-3309c393a076/download
- https://link.springer.com/content/pdf/10.1007/s10086-011-1181-2.pdf
- https://bioresources.cnr.ncsu.edu/resources/accuracy-of-predicting-the-moisture-content-of-three-types-of-wood-sections-using-near-infrared-spectroscopy/
- https://www.fpl.fs.usda.gov/documnts/pdf2024/fpl_2024_thapa001.pdf
- https://iris.univpm.it/bitstream/11566/314095/7/JFUE-D-22-00868_R1.pdf
- https://www.sciencedirect.com/science/article/abs/pii/S0026265X21009255
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140688
- https://pubmed.ncbi.nlm.nih.gov/29722978/
- https://soilspectroscopy.org/community-data-science-competition-results/
- https://opg.optica.org/as/abstract.cfm?uri=as-54-3-413
- https://www.sciencedirect.com/science/article/abs/pii/S0003267009008332
- https://www.sciencedirect.com/science/article/abs/pii/S0169743919307506
- https://www.sciencedirect.com/science/article/abs/pii/S0169743910000493
