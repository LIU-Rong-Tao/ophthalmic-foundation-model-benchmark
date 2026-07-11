from ophbench.registry.validator import validate_registry

if __name__ == "__main__":
    models, checkpoints, warnings = validate_registry()
    print(
        f"Valid registry: {len(models)} models, {len(checkpoints)} checkpoints, "
        f"{len(warnings)} warnings"
    )
