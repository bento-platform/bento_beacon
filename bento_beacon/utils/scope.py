def scoped_route_decorator_generator(blueprint):
    """
    # Generates a decorator equivalent to two flask "@route" decorators, one with a project_id prefix, and one without

    # input: a flask blueprint (all beacon routes belong to a particular blueprint)

    # output: a decorator that's equivalent to invoking these two flask decorators together:
        # @my_blueprint.route("my_route", **options)
        # @my_blueprint.route("/<project_id>/my_route", **options)
    """

    def scoped_route(rule, **options):
        def deco(f):
            blueprint.add_url_rule(rule, view_func=f, **options)
            blueprint.add_url_rule(f"/<project_id>{rule}", view_func=f, **options)

            async def wrappper(*args, **kwargs):
                return await f(*args, **kwargs)

            return wrappper

        return deco

    return scoped_route
