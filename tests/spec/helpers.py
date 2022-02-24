def transpose(results):
    keys = [k for k in results[0] if k != "patient_id"]
    return {k: {r["patient_id"]: r[k] for r in results} for k in keys}
