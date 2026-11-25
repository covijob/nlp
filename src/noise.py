def yra_triuksmas(tekstas):
    return False


def pazymeti(fragmentai):
    for fragmentas in fragmentai:
        fragmentas["triuksmas"] = yra_triuksmas(fragmentas["tekstas"])
    return fragmentai
