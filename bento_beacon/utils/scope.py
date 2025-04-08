from flask import request
from .katsu_utils import katsu_projects
from .exceptions import InvalidQuery

MESSAGE_FOR_TOO_MANY_DATASETS = "'datasetIds' field currently cannot take more than one dataset id"


def scoped_route_decorator_for_blueprint(blueprint):
    """
    Generates a decorator equivalent to two flask "@route" decorators, one with a project_id prefix, and one without.

    input: a flask blueprint (all beacon routes belong to a particular blueprint)

    output: a decorator that's equivalent to invoking these two flask decorators together:
        @my_blueprint.route("/my_route", **options)
        @my_blueprint.route("/<project_id>/my_route", **options)
    """

    def scoped_route(rule, **options):
        def deco(f):
            blueprint.add_url_rule(rule, view_func=f, **options)
            blueprint.add_url_rule(f"/<project_id>{rule}", view_func=f, **options)

            async def wrapper(*args, **kwargs):
                return await f(*args, **kwargs)

            return wrapper

        return deco

    return scoped_route


# used by info endpoints that don't check censorship settings
async def verify_request_project_scope() -> None:
    view_args = request.view_args if request.view_args else {}
    project_id = view_args.get("project_id")
    project_ids = [p["identifier"] for p in (await katsu_projects()).get("results", [])]
    if project_id is not None and project_id not in project_ids:
        raise InvalidQuery(f"No project found with id {project_id}")
