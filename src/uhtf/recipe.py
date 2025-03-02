#!/usr/bin/env python
# -*- coding: utf-8

"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Recipe endpoints.
"""

from quart import Blueprint
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from .authorize import login_required
from .database import get_db

recipe = Blueprint("recipe", __name__)


@recipe.get("/recipe")
@login_required
async def read() -> tuple:
    """Read recipes callback."""

    number = request.args.get("number")
    commands = get_db().execute(
        """
        SELECT * FROM command
        """
    ).fetchall()
    instruments = get_db().execute(
        """
        SELECT * FROM instrument
        """
    ).fetchall()
    measurements = get_db().execute(
        """
        SELECT * FROM measurement
        """
    ).fetchall()
    parts = get_db().execute(
        """
        SELECT * FROM part
        """
    ).fetchall()
    phases = get_db().execute(
        """
        SELECT * FROM phase
        """
    ).fetchall()
    procedures = get_db().execute(
        """
        SELECT * FROM procedure
        """
    ).fetchall()
    query = """
        SELECT
            recipe.id AS id,
            part.id AS part_id,
            part.name AS part,
            instrument.id AS instrument_id,
            instrument.name AS instrument,
            command.id AS command_id,
            command.name AS command,
            measurement.id AS measurement_id,
            measurement.name AS measurement,
            phase.id AS phase_id,
            phase.name AS phase,
            procedure.id AS procedure_id,
            procedure.name AS procedure
        FROM
            recipe
        INNER JOIN
            command ON command.id = recipe.command_id
        INNER JOIN
            instrument ON instrument.id = recipe.instrument_id
        OUTER LEFT JOIN
            measurement ON measurement.id = recipe.measurement_id
        INNER JOIN
            part ON part.id = recipe.part_id
        INNER JOIN
            phase ON phase.id = recipe.phase_id
        INNER JOIN
            procedure ON procedure.id = recipe.procedure_id 
        """
    name = request.args.get("name")
    if isinstance(name, str):
        query += f" WHERE part.name = '{name}'"
    recipes = get_db().execute(query).fetchall()
    return await render_template(
        "recipe.html",
        commands=commands,
        instruments=instruments,
        measurements=measurements,
        parts=parts,
        phases=phases,
        procedures=procedures,
        recipes=recipes,
        name=name,
    )


@recipe.post("/recipe")
@login_required
async def create() -> tuple:
    """Create recipe callback."""

    form = (await request.form).copy().to_dict() 
    form["measurement_id"] = form.get("measurement_id")
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO recipe (
                instrument_id,
                command_id,
                measurement_id,
                part_id,
                phase_id,
                procedure_id
            ) VALUES (
                :instrument_id,
                :command_id,
                :measurement_id,
                :part_id,
                :phase_id,
                :procedure_id
            )
            """,
            form
        )
        db.commit()
    except db.ProgrammingError:
        print("Missing parameter(s)")
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        print("Invalid parameter(s)")
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))


@recipe.post("/recipe/delete")
@login_required
async def delete():
    """Delete recipes callback."""

    db = get_db()
    form = await request.form
    recipe_ids = form.getlist("recipe_id")
    for recipe_id in recipe_ids:
        db.execute(
            "DELETE FROM recipe WHERE id = ?",
            (recipe_id,)
        )
        db.commit()
    return redirect(url_for(".read"))


@recipe.post("/recipe/update")
@login_required
async def update():
    """Update recipe endpoint."""

    form = (await request.form).copy().to_dict()
    form["measurement_id"] = form.get("measurement_id")
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE recipe SET
                updated_at = CURRENT_TIMESTAMP,
                command_id = :command_id,
                instrument_id = :instrument_id,
                measurement_id = :measurement_id,
                part_id = :part_id,
                phase_id = :phase_id,
                procedure_id = :procedure_id
            WHERE id = :id
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    return redirect(url_for(".read"))
