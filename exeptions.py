class BlueprintNotFound(Exception):
        def __init__(self,blueprint) -> None:
            self.message = "The blueprint %d does not exist on steam workshop" % blueprint.id
            super().__init__(self.message)