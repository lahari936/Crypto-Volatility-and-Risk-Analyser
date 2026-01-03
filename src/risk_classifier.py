def classify_risk(annual_vol):
    if annual_vol>0.7:
        return "High Risk"
    elif annual_vol>0.4:
        return "Medium Risk"
    else:
        return "Low Risk"