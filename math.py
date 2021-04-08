import math, cmath
import asyncio

from pyrogram import filters

from bot import alemiBot

from util import batchify
from util.permission import is_allowed
from util.message import edit_or_reply
from util.command import filterCommand
from util.decorators import report_error, set_offline
from util.help import HelpCategory

import sympy
from sympy.solvers import solve
from sympy.plotting import plot3d, plot3d_parametric_line
from sympy.parsing.sympy_parser import parse_expr
from sympy import preview, plot

import logging
logger = logging.getLogger(__name__)

# This is maybe should be in the statistics module? I dunno, lmk if it fits in tricks
HELP = HelpCategory("MATH")

HELP.add_help(["expr", "math"], "convert to LaTeX formula",
				"this command accepts sympy syntax and will spit out a LaTeX formula as image. " +
				"You can add the `-latex` argument and pass LaTeX directly.", args="[-latex] <expr>", public=True)
@alemiBot.on_message(is_allowed & filterCommand(["expr", "math"], list(alemiBot.prefixes), flags=["-latex"]))
@report_error(logger)
@set_offline
async def expr(client, message):
	args = message.command
	if "arg" not in args:
		return # nothing to do!
	expr = args["arg"]
	logger.info(f"Mathifying \'{expr}\'")
	await client.send_chat_action(message.chat.id, "upload_document")
	if "-latex" in args["flags"]:
		preview(expr, viewer='file', filename='expr.png', dvioptions=["-T", "bbox", "-D 300", "--truecolor", "-bg", "Transparent"])
	else:
		res = parse_expr(expr)
		preview(res, viewer='file', filename='expr.png', dvioptions=["-T", "bbox", "-D 300", "--truecolor", "-bg", "Transparent"])
	await client.send_photo(message.chat.id, "expr.png", reply_to_message_id=message.message_id,
									caption=f"` → {expr} `")
	await client.send_chat_action(message.chat.id, "cancel")

HELP.add_help(["plot", "graph"], "plot provided function",
				"this command will run sympy `plot` and return result as image. Foruma passing is wonky. " +
				"You can add the `-3d` argument to plot in 3d.", args="[-3d] <expr>", public=True)
@alemiBot.on_message(is_allowed & filterCommand(["plot", "graph"], list(alemiBot.prefixes), flags=["-3d"]))
@report_error(logger)
@set_offline
async def graph(client, message):
	args = message.command
	if "arg" not in args:
		return # nothing to plot
	await client.send_chat_action(message.chat.id, "upload_document")
	expr = args["arg"]
	logger.info(f"Plotting \'{expr}\'")
	eq = []
	for a in expr.split(", "):
		eq.append(parse_expr(a).simplify())

	if "-3d" in args["flags"]:
		plot3d(*eq, show=False).save("graph.png")
	else:
		plot(*eq, show=False).save("graph.png")
	
	await client.send_photo(message.chat.id, "graph.png", reply_to_message_id=message.message_id,
									caption=f"` → {eq} `")
	await client.send_chat_action(message.chat.id, "cancel")

HELP.add_help("solve", "attempt to solve equation",
				"this command will run sympy `solve` and attempt to find roots of the " +
				"equation. You can pass systems too! Add flag `-simpl` to simplify your input " +
				"(won't work with systems)", args="[-simpl] <expr>", public=True)
@alemiBot.on_message(is_allowed & filterCommand("solve", list(alemiBot.prefixes), flags=["-simpl"]))
@report_error(logger)
@set_offline
async def solve_cmd(client, message):
	if "arg" not in message.command:
		return await edit_or_reply(message, "`[!] → ` No arg given")
	expr = message.command["arg"]
	logger.info(f"Solving \'{expr}\'")
	in_expr = parse_expr(expr).simplify()
	res = solve(in_expr)
	out = f"` → {str(in_expr)}`\n```" + str(res) + "```"
	await edit_or_reply(message, out)
