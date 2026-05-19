# FieldSense

**Prediction of Electric Fields of UHV AC Transmission Lines 
using Machine Learning Techniques**

> Built as part of B.Tech ECE coursework at MGIT, Hyderabad.

---

## What is this?

UHV transmission lines (1200 kV and above) produce strong electric 
fields at ground level that must stay within WHO/IEC safety limits 
(5 kV/m). Calculating these fields traditionally requires building 
and inverting Maxwell's potential coefficient matrix — accurate but 
slow for real-time or repeated use.

FieldSense replaces that computation with a trained ML model that 
predicts ground-level electric field strength instantly, given any 
line configuration.

---

## How it works

**Phase 1 — Dataset Generation**  
The analytical method (Maxwell's [P] matrix → inversion → K 
coefficients → E-field) is implemented in Python and swept across 
thousands of line configurations to generate labeled training data.

**Phase 2 — ML Model**  
Three models are trained and compared — ANN, Random Forest, and SVR. 
The best model achieves R² > 0.98 against the analytical solution.

---

## Validated Against
1200 kV, 3-phase line | N=8 bundle | H=37m | Phase spacing=24m

---

## Stack
Python · NumPy · Pandas · scikit-learn · TensorFlow · Matplotlib

---

## Files
| File | Purpose |
|------|---------|
| `analytical.py` | Physics engine — computes [P], [M], E-field |
| `dataset_generator.py` | Generates training dataset |
| `ml_model.py` | Trains and evaluates ML models |
| `predict.py` | Prediction interface |
| `compare.py` | Analytical vs ML comparison plot |
| `index.html` | FieldSense website — Matrix theme |
| `index_claude.html` | FieldSense website — Claude theme |

---

## Team
B.Tech ECE — MGIT Hyderabad, 2026
