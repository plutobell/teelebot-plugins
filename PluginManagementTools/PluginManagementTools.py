# -*- coding:utf-8 -*-
"""
@description: Plugin Management Tools
@creation date: 2021-06-23
@last modification: 2023-05-15
@author: Pluto (github.com/plutobell)
"""
import os
import sys
import shutil
import tarfile
import subprocess
from platform import system as system_type

import requests
requests.packages.urllib3.disable_warnings()

def PluginManagementTools(bot, message):

    root_id = bot.root_id
    version = bot.version
    plugin_dir = bot.plugin_dir
    plugin_bridge = bot.plugin_bridge
    proxies = bot.proxies

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    message_type = message["message_type"]
    if message_type == "text":
        text = message["text"]

    prefix = ""
    ok, metadata = bot.metadata.read()
    if ok:
        prefix = metadata.get("Command", "")

    if str(user_id) != str(root_id):
        msg = "无权限。"
        status = bot.sendMessage(chat_id=chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(60, chat_id, status["message_id"])
        return

    if not os.path.exists(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache")):
        os.mkdir(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache"))

    if not os.path.exists(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/sources_cache")):
        os.mkdir(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/sources_cache"))

    sources_dict = {
        "official": "https://github.com/plutobell/teelebot-plugins"
    }
    if not os.path.exists(bot.path_converter(bot.plugin_dir + "PluginManagementTools/sources.list")):
        with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/sources.list"), "w", encoding="utf-8") as sources:
            sources.writelines(["official " + sources_dict["official"]])
    now_plugins_cache_dir_list = os.listdir(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/sources_cache"))
    with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/sources.list"), "r", encoding="utf-8") as sources:
        lines = sources.readlines()
        for line in lines:
            line_list = line.strip("\n").split(" ")
            if line_list[0] not in now_plugins_cache_dir_list:
                if os.path.exists(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time")):
                    os.remove(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time"))

            if line_list[0] == "official" and \
                line_list[1] != sources_dict["official"]:
                sources_dict[line_list[0]] = sources_dict["official"]
            else:
                sources_dict[line_list[0]] = line_list[1]

    updated_old_dict = {}
    if not os.path.exists(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time")):
        with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time"), "w", encoding="utf-8") as updated_time:
            write_list = []
            for label in sources_dict.keys():
                write_list.append(label + " " + "2007-10-01T25:61:61Z\n")
            updated_time.writelines(write_list)
    with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time"), "r", encoding="utf-8") as updated_time:
        lines = updated_time.readlines()
        for line in lines:
            line_list = line.strip("\n").split(" ")
            updated_old_dict[line_list[0]] = line_list[1]
    with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time"), "w", encoding="utf-8") as updated_time:
        write_list = []
        for label in sources_dict.keys():
            if label not in updated_old_dict.keys():
                updated_old_dict[label] = "2007-10-01T25:61:61Z"
                write_list.append(label + " " + "2007-10-01T25:61:61Z\n")
            else:
                write_list.append(label + " " + updated_old_dict[label] + "\n")
        updated_time.writelines(write_list)

    cache_path = bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/")
    sources_cache_path = bot.path_converter(cache_path + "/sources_cache/")

    commands_dict = {
        "add-source": "添加源，格式：add-source label url",
        "del-source": "删除源，格式：del-source label",
        "list-sources": "查看源列表",
        "update": "更新索引缓存",
        "upgrade": "更新插件包",
        "clean": "清除本地缓存",
        "add": "安装插件，默认使用官方源，使用源标签指定源，格式：add label/Plugin",
        "del": "卸载插件，同时指定参数 -d 以移除依赖，格式：del -d Plugin",
        "list": "查看已安装插件",
        "search": "搜索插件，默认在所有源中搜索，使用源标签搜索特定源，格式：search label/Plugin",
        "show": "查看插件信息，默认查看本地插件，使用源标签查看特定源，格式：show label/Plugin",
    }

    argument_list = text.split(" ", 1)
    if len(argument_list) == 1:
        msg = "<b>PluginManagementTools 插件功能</b>\n\n"
        for command, description in commands_dict.items():
            msg += "<b>" + prefix + " " + command + "</b> " + description + "\n"
        bot.sendChatAction(chat_id=chat_id, action="typing")
        status = bot.sendMessage(chat_id=chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(60, chat_id, status["message_id"])
    elif len(argument_list) == 2:
        sub_argument_list = argument_list[1].split(" ", 1)
        command = sub_argument_list[0]
        if len(sub_argument_list) == 1:
            command_argument = None
        elif len(sub_argument_list) == 2:
            command_argument = sub_argument_list[1]

        if command not in commands_dict.keys():
            bot.sendChatAction(chat_id=chat_id, action="typing")
            msg = "指令 <b>" + command + "</b> 不存在。"
            status = bot.sendMessage(chat_id=chat_id, text=msg,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
            return

        pip = PipExecutor()
        github = GithubAPI(proxies=proxies)

        if command == "add-source" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) == 2:
                label = arg_list[0]
                url = arg_list[1]

                if url in sources_dict.values():
                    for source_label, source_url in sources_dict.items():
                        if url.strip(os.sep) == source_url.strip(os.sep):
                            label = source_label
                    msg = "源地址已存在：\n" + label + " " + url
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id,
                        text="<code>"+msg+"</code>", parse_mode="HTML",
                        reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                elif label in sources_dict.keys():
                    msg = "标签 " + label + " 已存在：\n" + label + " " + sources_dict[label]
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id,
                        text="<code>"+msg+"</code>", parse_mode="HTML",
                        reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                else:
                    if len(url.split("github.com/")[1].strip("/").split("/")) != 2:
                        msg = "源地址格式错误"
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return
                    if "github.com/" not in url:
                        msg = "源仅支持 GitHub 仓库地址"
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return

                    sources_dict[label] = url.strip("/")

                    write_list = []
                    for source_label, source_url in sources_dict.items():
                        write_list.append(source_label + " " + source_url + "\n")

                    try:
                        with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/sources.list"), "w", encoding="utf-8") as sources:
                            sources.writelines(write_list)
                        msg = "成功添加以下源：\n" + label + " " + sources_dict[label]
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                    except:
                        msg = "以下源添加失败：\n" + label + " " + sources_dict[label]
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif command == "del-source" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) == 1:
                label = arg_list[0]
                if label in sources_dict.keys():
                    deleted_url = sources_dict[label]
                    sources_dict.pop(label)

                    write_list = []
                    for source_label, source_url in sources_dict.items():
                        write_list.append(source_label + " " + source_url + "\n")

                    try:
                        with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/sources.list"), "w", encoding="utf-8") as sources:
                            sources.writelines(write_list)
                        msg = "成功移除以下源：\n" + label + " " + deleted_url
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                    except:
                        msg = "移除标签为 " + label + " 的源失败"
                        bot.sendChatAction(chat_id=chat_id, action="typing")
                        status = bot.sendMessage(chat_id=chat_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML",
                            reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                else:
                    msg = "标签 " + label + " 不存在"
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id,
                        text="<code>"+msg+"</code>", parse_mode="HTML",
                        reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif command == "list-sources":
            msg = "Sources List\n\n"

            i = 1
            for label, url in sources_dict.items():
                msg += "[" + str(i) + "]" + label + " " + url + "\n\n"
                i += 1
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id,
                text="<code>"+msg+"</code>", parse_mode="HTML",
                reply_to_message_id=message_id)
            gap = len(sources_dict) * 2 + 30
            bot.message_deletor(gap, chat_id, status["message_id"])

        elif command == "update":
            msg = "开始更新索引缓存\n"
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                parse_mode="HTML", reply_to_message_id=message_id)
            update_msg_id = status["message_id"]

            msg += "正在同步源 ..."
            bot.editMessageText(chat_id=chat_id,
                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
            sources_info_dict = {}
            for label, url in sources_dict.items():
                url_list = url.strip("/").split("github.com/")[1]
                username_and_reponame = url_list.split("/")
                username = username_and_reponame[0]
                repo_name = username_and_reponame[1]
                ok, result = github.repo_detail_info(username=username,
                    repo_name=repo_name)
                # print(ok, result)
                if ok:
                    updated_new = str(result["pushed_at"])
                    default_branch = result["default_branch"]
                    sources_info_dict[label] = {
                        "updated_new": updated_new,
                        "default_branch": default_branch,
                        "username": username,
                        "repo_name": repo_name
                    }
                elif result == "Not Found":
                    msg += "Done\n同步源 " + label + " **Unreachable** "
                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

            # print(sources_info_dict)
            changed_sources_list = []
            for label, info in sources_info_dict.items():
                updated_new = info["updated_new"]
                default_branch = info["default_branch"]
                username = info["username"]
                repo_name = info["repo_name"]

                if updated_new != updated_old_dict[label]:
                    msg += "Done\n同步源 " + label + " ..."
                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                    updated_old_dict[label] = updated_new
                    changed_sources_list.append(label)
                    ok, result = github.download_archive_file(
                        username=username,
                        repo_name=repo_name,
                        branch=default_branch)
                    if ok:
                        tar_file_path = sources_cache_path + repo_name + "-" + default_branch + ".tar.gz"
                        with open(tar_file_path, "wb") as tar:
                            tar.write(result)
                        shutil.rmtree(path=sources_cache_path + os.sep + label,
                            ignore_errors=True, onerror=None)
                        extract_file(file=tar_file_path,
                            saved_path=sources_cache_path)
                        os.rename(sources_cache_path + os.sep + repo_name + "-" + default_branch,
                            sources_cache_path + os.sep + label)
                        if os.path.exists(tar_file_path):
                            os.remove(path=tar_file_path)

            with open(bot.path_converter(bot.plugin_dir + "PluginManagementTools/.cache/updated-time"), "w", encoding="utf-8") as updated_time:
                write_list = []
                for label, date in updated_old_dict.items():
                    write_list.append(label + " " + date  + "\n")
                updated_time.writelines(write_list)

            msg += "Done\n同步完成，共更新了 " + str(len(changed_sources_list)) + " 个源"
            bot.editMessageText(chat_id=chat_id,
                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

            msg += "\n正在查询可更新的插件 ..."
            bot.editMessageText(chat_id=chat_id,
                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

            all_can_upgrade_plugins = []
            for label in sources_info_dict.keys():
                can_upgrade_plugins = checking_plugins_can_upgrade(bot, 
                    plugins=plugin_bridge.keys(), plugin_dir=plugin_dir,
                    sources_cache_path=sources_cache_path, label=label,
                    source_url=sources_dict[label], bot_version=version)

                msg += "Done\n源 " + label + " 有 " + str(len(can_upgrade_plugins)) + " 个插件可更新 ..."
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                all_can_upgrade_plugins.extend(can_upgrade_plugins)

            if len(all_can_upgrade_plugins) != 0:
                msg += "Done\n\n以下插件可被更新: \n"
                for plugin in all_can_upgrade_plugins:
                    msg += plugin["name"] +" v" + plugin["old_version"] + \
                        "->v" + plugin["new_version"] + "\n"
                msg += '\n使用指令"' + prefix + ' upgrade"进行更新'
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
            else:
                msg += "Done\n所有插件已保持最新\n"
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
            bot.message_deletor(30, chat_id, update_msg_id)

            with open(cache_path + os.sep + "can_upgrade", "w", encoding="utf-8") as can_upgrade:
                write_list = []
                for plugin in all_can_upgrade_plugins:
                    write_list.append(plugin["name"] + " " + plugin["old_version"] + " " + plugin["new_version"] + "\n")
                can_upgrade.writelines(write_list)

        elif command == "upgrade":
            msg = "开始检查更新插件\n"
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                parse_mode="HTML", reply_to_message_id=message_id)
            update_msg_id = status["message_id"]

            msg += "正在查询可更新的插件 ..."
            bot.editMessageText(chat_id=chat_id,
                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
            # bot.message_deletor(30, chat_id, update_msg_id)
            all_can_upgrade_plugins = []
            if not os.path.exists(cache_path + os.sep + "can_upgrade"):
                msg += 'Done\n未找到缓存文件\n请先使用指令"'+ prefix + ' update"更新索引'
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(15, chat_id, update_msg_id)
                return
            with open(cache_path + os.sep + "can_upgrade", "r", encoding="utf-8") as can_upgrade:
                lines = can_upgrade.readlines()
                if len(lines) == 0 or (len(lines) == 1 and lines[0].strip("\n") in ["", None]):
                    msg += "Done\n所有插件已保持最新\n"
                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                    bot.message_deletor(15, chat_id, update_msg_id)
                    return
                else:
                    for line in lines:
                        line_list = line.strip("\n").split(" ")
                        all_can_upgrade_plugins.append({
                            "name": line_list[0],
                            "old_version": line_list[1],
                            "new_version": line_list[2]
                        })

            if len(all_can_upgrade_plugins) != 0:
                msg += "Done\n共有 "+ str(len(all_can_upgrade_plugins)) + " 个插件可被更新\n" +\
                    "准备更新插件 ..."
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                for plugin in all_can_upgrade_plugins:
                    msg += "Done\n更新插件 " + plugin["name"] +" v" + plugin["old_version"] + \
                        "->v" + plugin["new_version"] + " ..."
                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                    label = plugin["name"].split("/")[0]
                    plugin_name = plugin["name"].split("/")[1]
                    upgrade_plugin(plugin_name=plugin_name,
                        source_cache_dir=sources_cache_path + os.sep + label + os.sep,
                        plugin_dir=plugin_dir
                    )

                os.remove(cache_path + os.sep + "can_upgrade")
                msg += 'Done\n'
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(30, chat_id, update_msg_id)
        elif command == "clean":
            msg = "正在清除本地缓存 ..."
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                parse_mode="HTML", reply_to_message_id=message_id)
            update_msg_id = status["message_id"]

            try:
                if os.path.exists(cache_path):
                    shutil.rmtree(path=cache_path,
                        ignore_errors=True, onerror=None)

                msg += "Done\n"
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(15, chat_id, update_msg_id)
            except:
                msg += "Error\n清理缓存失败"
                bot.editMessageText(chat_id=chat_id,
                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(15, chat_id, update_msg_id)

        elif command == "add" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) >= 1:
                msg = "开始安装插件\n"
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                    parse_mode="HTML", reply_to_message_id=message_id)
                update_msg_id = status["message_id"]

                plugin_name_list = arg_list
                for plugin_name_raw in plugin_name_list:
                    plugin_name = plugin_name_raw
                    label = "official" # 没有指定源标签时默认使用官方源
                    if len(plugin_name_raw.split("/")) == 2:
                        plugin_name = plugin_name_raw.split("/")[1]
                        label = plugin_name_raw.split("/")[0]

                    if label in sources_dict.keys() \
                        and not os.path.exists(sources_cache_path + os.sep + label):
                        msg += "安装插件 " + label + "/" + plugin_name + " ...Skip[Source not sync]\n"
                        bot.editMessageText(chat_id=chat_id,
                            message_id=update_msg_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML")
                        continue
                    elif label not in sources_dict.keys():
                        msg += "安装插件 " + label + "/" + plugin_name + " ...Skip[Source not found]\n"
                        bot.editMessageText(chat_id=chat_id,
                            message_id=update_msg_id,
                            text="<code>"+msg+"</code>", parse_mode="HTML")
                        continue

                    source_plugin_list = []
                    source_dir_list_raw = os.listdir(sources_cache_path + os.sep + label)
                    for item in source_dir_list_raw:
                        if os.path.isdir(sources_cache_path + os.sep + label + os.sep + item):
                            source_plugin_list.append(item)

                    if plugin_name in plugin_bridge.keys():
                        ok, metadata = get_metadata(bot, plugin_dir, plugin_name, version)
                    elif plugin_name in source_plugin_list:
                        ok, metadata = get_metadata(bot,
                            sources_cache_path + os.sep + label + os.sep,
                            plugin_name, version)
                    else:
                        ok = False

                    if ok:
                        for source_label, url in sources_dict.items():
                            if url.strip(os.sep) == metadata["Source"].strip(os.sep):
                                label = source_label
                        msg += "安装插件 " + label + "/" + plugin_name + " " + metadata["Version"] + " ..."
                    else:
                        msg += "安装插件 " + label + "/" + plugin_name + " ..."
                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                    if ok:
                        requires_teelebot = metadata["Requires-teelebot"].strip(" ").replace(" ", "")
                        requires_teelebot = requires_teelebot.replace(">", "")
                        requires_teelebot = requires_teelebot.replace("<", "")
                        requires_teelebot = requires_teelebot.replace("=", "")

                    if plugin_name in plugin_bridge.keys():
                        msg += "Skip[Already existed]\n"
                    elif plugin_name not in source_plugin_list:
                        msg += "Skip[Not found]\n"
                    elif ok and requires_teelebot > version:
                        msg += "Skip[Requires teelebot >=" + requires_teelebot + "]\n"
                    else:
                        try:

                            if ok:
                                uninstalled_dependencies = []
                                dependencies_raw = metadata["Requires-dist"].strip(" ").replace(" ", "").split(",")
                                dependencies = []
                                for dependency in dependencies_raw:
                                    if dependency not in ["", " ", None]:
                                        dependencies.append(dependency)
                                dependency_total = len(dependencies)

                                if dependency_total > 0:
                                    msg += "\n"

                                for i, dependency in enumerate(dependencies):
                                    msg += "[" + str(i+1) + "/" + str(dependency_total) + "]为 " + label + "/" + plugin_name + " 安装依赖 " + dependency + " ..."
                                    bot.editMessageText(chat_id=chat_id,
                                        message_id=update_msg_id,
                                        text="<code>"+msg+"</code>", parse_mode="HTML")

                                    ok, result = pip.install([dependency,])
                                    if not ok:
                                        uninstalled_dependencies.append(dependency)
                                        msg += "Failure\n"
                                    else:
                                        msg += "Success\n"

                                if len(uninstalled_dependencies) != 0:
                                    msg += "** 插件 " + label + "/" + plugin_name + " 依赖缺失，安装失败 **\n"
                                else:
                                    try:
                                        copy = Copy()
                                        copy.copyTree(
                                            sources_cache_path + os.sep + label + os.sep + plugin_name,
                                            plugin_dir + plugin_name
                                        )
                                        if dependency_total == 0:
                                            msg += "Success\n"
                                    except:
                                        msg += "** 插件 " + label + "/" + plugin_name + " 安装失败 **\n"
                            else:
                                msg += "Failure[Dependency Information]\n"
                        except:
                            msg += "Failure[Dependency Installation]\n"

                    bot.editMessageText(chat_id=chat_id,
                        message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(30, chat_id, status["message_id"])

            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif command == "del" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) >= 1:
                if len(arg_list) == 1 and arg_list[0].strip(" ").replace(" ", "") in ["-d", "-dependency"]:
                    bot.sendChatAction(chat_id=chat_id, action="typing")
                    status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                        parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return

                delete_dependency = False
                if len(arg_list) > 1 \
                    and arg_list[0].strip(" ").replace(" ", "") in ["-d", "-dependency"]:
                    delete_dependency = True
                    arg_list = arg_list[1:]

                msg = "开始卸载插件\n"
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                    parse_mode="HTML", reply_to_message_id=message_id)
                update_msg_id = status["message_id"]

                plugin_name_list = arg_list
                for plugin_name_raw in plugin_name_list:
                    plugin_name = plugin_name_raw
                    label = None
                    # if len(plugin_name_raw.split("/")) == 2:
                    #     plugin_name = plugin_name_raw.split("/")[1]
                    #     label = plugin_name_raw.split("/")[0]

                    if plugin_name not in plugin_bridge.keys() \
                        or not os.path.exists(plugin_dir + plugin_name):
                        msg += "卸载插件 " + plugin_name + " ...Skip[Not installed]\n"
                        bot.editMessageText(chat_id=chat_id,
                            message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                    else:
                        ok, metadata = get_metadata(bot, plugin_dir, plugin_name, version)

                        if ok and label is None:
                            for source_label, url in sources_dict.items():
                                if url.strip(os.sep) == metadata["Source"].strip(os.sep):
                                    label = source_label

                        if ok and label is not None:
                            msg += "卸载插件 " + label + "/" + plugin_name + " " + metadata["Version"] + " ..."
                        else:
                            msg += "卸载插件 " + plugin_name + " ..."

                        bot.editMessageText(chat_id=chat_id,
                                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                        try:
                            shutil.rmtree(path=plugin_dir + plugin_name,
                                ignore_errors=True, onerror=None)
                            msg += "Success\n"
                        except:
                            msg += "Failure\n"

                        bot.editMessageText(chat_id=chat_id,
                                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                        if delete_dependency:
                            dependencies = metadata["Requires-dist"].strip(" ").replace(" ", "").split(",")
                            i = 0
                            total = len(dependencies)
                            for dependency in dependencies:
                                if dependency in ["", " ", None]:
                                    if total > 0:
                                        total -= 1
                                    continue
                                else:
                                    i += 1

                                if label is not None:
                                    msg += "[" + str(i) + "/" + str(total) + "]为 " + label + "/" + plugin_name + " 卸载依赖 " + dependency + " ..."
                                else:
                                    msg += "[" + str(i) + "/" + str(total) + "]为 " + plugin_name + " 卸载依赖 " + dependency + " ..."
                                bot.editMessageText(chat_id=chat_id,
                                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")

                                ok, result = pip.uninstall([dependency,])
                                if not ok:
                                    msg += "Failure\n"
                                else:
                                    msg += "Success\n"

                                bot.editMessageText(chat_id=chat_id,
                                    message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                        else:
                            if ok and label is not None:
                                msg += "为 " + label + "/" + plugin_name + " 卸载依赖  ...Skip\n"
                            else:
                                msg += "为 " + plugin_name + " 卸载依赖  ...Skip\n"

                            bot.editMessageText(chat_id=chat_id,
                                message_id=update_msg_id, text="<code>"+msg+"</code>", parse_mode="HTML")
                bot.message_deletor(30, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif command == "list":
            msg = "已安装 "+ str(len(plugin_bridge.keys())) +" 个插件:\n"
            for i, plugin in enumerate(sorted(plugin_bridge.keys())):
                ok, metadata = get_metadata(bot, plugin_dir, plugin, version)
                if ok:
                    label = ""
                    for label_tmp, url in sources_dict.items():
                        if metadata["Source"].strip(os.sep) == label_tmp.strip(os.sep):
                            label = label_tmp
                    if label != "":
                        msg += "[" + str(i+1) + "]" + label + "/" + plugin + " v" + metadata["Version"] + "\n"
                    else:
                        msg += "[" + str(i+1) + "]" + plugin + " v" + metadata["Version"] + "\n"
                else:
                    msg += "[" + str(i+1) + "]" + plugin + "\n"

            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                parse_mode="HTML", reply_to_message_id=message_id)
            gap = len(plugin_bridge) * 2 + 30
            bot.message_deletor(gap, chat_id, status["message_id"])

        elif command == "search" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) == 1:
                keywords_raw = arg_list[0].strip(" ").replace(" ", "")
                keywords = keywords_raw
                label = None
                if len(keywords_raw.split("/")) == 2:
                    keywords = keywords_raw.split("/")[1]
                    label = keywords_raw.split("/")[0]

                search_result = {}
                search_source_label_list = []
                if label is None:
                    search_source_label_list.extend(sources_dict.keys())
                else:
                    search_source_label_list.append(label)

                for search_label in search_source_label_list:
                    if not os.path.exists(sources_cache_path + os.sep + search_label):
                        continue

                    source_plugin_list = []
                    source_dir_list_raw = os.listdir(sources_cache_path + os.sep + search_label)
                    for item in source_dir_list_raw:
                        if os.path.isdir(sources_cache_path + os.sep + search_label + os.sep + item):
                            source_plugin_list.append(item)

                    for plugin in source_plugin_list:
                        ok, metadata = get_metadata(bot, 
                            sources_cache_path + os.sep + search_label + os.sep,
                            plugin, version)
                        if ok:
                            if keywords.lower() in plugin.lower() \
                                or plugin.lower() in keywords.lower() \
                                or keywords.lower() in metadata["Summary"].lower() \
                                or keywords.lower() in metadata["Keywords"].lower():

                                search_result[search_label + "/" + plugin] = {
                                    "Version": metadata["Version"],
                                    "Source": metadata["Source"],
                                    "Summary": metadata["Summary"],
                                    "Status": ""
                                }

                                if plugin in plugin_bridge.keys():
                                    ok, metadata = get_metadata(bot, plugin_dir, plugin, version)
                                    if ok:
                                        if sources_dict[search_label].strip(os.sep) == metadata["Source"].strip(os.sep) \
                                            and search_result[search_label + "/" + plugin]["Source"] not in ["", None] \
                                            and metadata["Source"] not in ["", None]:
                                            search_result[search_label + "/" + plugin]["Status"] = "installed"
                        else:
                            search_result[search_label + "/" + plugin] = {
                                "Version": "",
                                "Source": "",
                                "Summary": "",
                                "Status": ""
                            }

                if label is None:
                    msg = "在所有源中的搜索结果如下:\n\n"
                else:
                    msg = "在源 " + label +" 中的搜索结果如下:\n\n"

                i = 1
                for plugin_name, info in search_result.items():
                    msg += "[" + str(i) + "]" + plugin_name + " " + info["Version"]
                    if info["Status"] == "installed":
                        msg += " [installed] " + "\n"
                    else:
                        msg += "\n"
                    msg += info["Summary"] + "\n\n"
                    i += 1

                if len(search_result) == 0:
                    msg += "抱歉，没有找到任何插件"

                status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                    parse_mode="HTML", reply_to_message_id=message_id)
                gap = len(search_result) * 2 + 30
                bot.message_deletor(gap, chat_id, status["message_id"])

            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif command == "show" and command_argument != None:
            arg_list = command_argument.split(" ")
            if len(arg_list) == 1:
                plugin_name_raw = arg_list[0].strip(" ").replace(" ", "")
                plugin_name = plugin_name_raw
                label = None
                if len(plugin_name_raw.split("/")) == 2:
                    plugin_name = plugin_name_raw.split("/")[1]
                    label = plugin_name_raw.split("/")[0]

                if label is None:
                    if plugin_name not in plugin_bridge.keys():
                        msg = "在本地未找到插件 " + plugin_name + "\n\n"
                        status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                            parse_mode="HTML", reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return
                else:
                    if not os.path.exists(sources_cache_path + os.sep + label):
                        if label not in sources_dict.keys():
                            msg = "标签 " + label + " 未找到\n" +\
                            '请使用指令"' + prefix +  ' add-source"' + "添加源后重试"
                        else:
                            msg = "在本地索引缓存中未找到源 " + label + "\n" + \
                                '请执行指令"' + prefix +  ' update"' + "更新索引缓存后重试"
                        status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                            parse_mode="HTML", reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return

                    source_dir_list = []
                    source_dir_list_raw = os.listdir(sources_cache_path + os.sep + label)
                    for item in source_dir_list_raw:
                        if os.path.isdir(sources_cache_path + os.sep + label + os.sep + item):
                            source_dir_list.append(item)
                    if plugin_name not in source_dir_list:
                        msg = "在源 " + label + " 中未找到插件 " + plugin_name + "\n\n"
                        status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                            parse_mode="HTML", reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return

                if label is None:
                    ok, metadata = get_metadata(bot, plugin_dir, plugin_name, version)
                else:
                    ok, metadata = get_metadata(bot, 
                        sources_cache_path + os.sep + label + os.sep,
                        plugin_name, version)

                if ok:
                    source_url = metadata["Source"]
                    if label is not None:
                        source_label = label
                    else:
                        source_label = ""
                    for s_label, s_url in sources_dict.items():
                        if s_url.strip("/n") == source_url.strip("/"):
                            source_label = s_label

                    metadata.pop("Metadata-version")
                    metadata.pop("Source")
                    metadata.pop("Keywords")
                    metadata.pop("Command")
                    metadata.pop("Buffer-permissions")

                    if label is not None:
                        msg = "源 "+ label +" 中的 " + plugin_name + " 插件的信息如下:\n\n"
                    else:
                        msg = "本地安装的 " + plugin_name + " 插件的信息如下:\n\n"

                    for key, value in metadata.items():
                        msg += key + ": " + value + "\n"

                    msg = msg.replace("Plugin-name:", "插件名称:")
                    msg = msg.replace("Version:", "版本信息:")
                    msg = msg.replace("Summary:", "简介信息:")
                    msg = msg.replace("Home-page:", "主页地址:")
                    msg = msg.replace("Author:", "作者名称:")
                    msg = msg.replace("Author-email:", "作者邮箱:")
                    msg = msg.replace("License:", "协议名称:")
                    msg = msg.replace("Requires-teelebot:", "框架版本:")
                    msg = msg.replace("Requires-dist:", "依赖列表:")

                    msg += "来源标签: " + source_label + "\n"

                    status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                        parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(60, chat_id, status["message_id"])
                else:
                    msg = "获取插件 " + plugin_name + " 的信息失败\n\n"
                    status = bot.sendMessage(chat_id=chat_id, text="<code>"+msg+"</code>",
                        parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
            else:
                bot.sendChatAction(chat_id=chat_id, action="typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                    parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        else:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误。",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])

def return_source_plugins(sources_cache_path, label):
    source_plugin_list =  os.listdir(sources_cache_path + os.sep + label)

    source_plugins = []
    for plugin in source_plugin_list:
        if os.path.isdir(sources_cache_path + os.sep + label + os.sep + plugin):
            source_plugins.append(plugin)

    return source_plugins

def checking_plugins_can_upgrade(bot, plugins, plugin_dir, sources_cache_path, label, source_url, bot_version):
    source_plugins = return_source_plugins(sources_cache_path, label)

    can_upgrade_plugins = []
    for plugin in plugins:
        plugin_info = {}
        if plugin in source_plugins:
            old_ok, old_metadata_dict = get_metadata(bot, plugin_dir, plugin, bot_version)
            new_ok, new_metadata_dict = get_metadata(bot, sources_cache_path + os.sep + label + os.sep, plugin, bot_version)
            if old_ok and new_ok:
                if old_metadata_dict["Version"] != new_metadata_dict["Version"]:
                    if old_metadata_dict["Source"].strip(os.sep) == \
                        new_metadata_dict["Source"].strip(os.sep) == \
                        source_url.strip(os.sep):
                        plugin_info["name"] = label + "/" + plugin
                        plugin_info["old_version"] = old_metadata_dict["Version"]
                        plugin_info["new_version"] = new_metadata_dict["Version"]
                        can_upgrade_plugins.append(plugin_info)

    return can_upgrade_plugins

def get_metadata(bot, plugin_dir, plugin_name, bot_version):
    '''Metadata-version: 1.1
    '''
    metadata_path = plugin_dir + plugin_name + os.sep + "METADATA"
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w", encoding='utf-8') as metadata:
            metadata.writelines([
                "Metadata-version: 1.1\n",
                "Plugin-name: " + plugin_name + "\n",
                "Command: /" + plugin_name.lower() + "\n",
                "Buffer-permissions: False:False\n",
                "Version: 0.1.0\n",
                "Summary: \n",
                "Home-page: \n",
                "Author: \n",
                "Author-email: \n",
                "License: \n",
                "Keywords: \n",
                "Requires-teelebot: >=" + bot_version + "\n",
                "Requires-dist: \n",
                "Source: "
            ])

    plugin_metadata_dict = {}
    ok, data = bot.metadata.read(plugin_name=plugin_name, plugin_dir=plugin_dir)
    if ok:
        plugin_metadata_dict = data

    if "Source" not in plugin_metadata_dict.keys():
        plugin_metadata_dict["Source"] = ""
        bot.metadata.write(
            plugin_name=plugin_name,
            metadata=plugin_metadata_dict,
            plugin_dir=plugin_dir
        )

    ok, data = bot.metadata.template()
    if len(plugin_metadata_dict) == len(data) and \
        "None" not in plugin_metadata_dict.keys():
        return True, plugin_metadata_dict
    else:
        return False, "Metadata format error."

def upgrade_plugin(plugin_name, source_cache_dir, plugin_dir):
    copy = Copy()
    copy.copyTree(
        source_cache_dir + plugin_name,
        plugin_dir + plugin_name,
    )

def extract_file(file, saved_path):
    tar = tarfile.open(file)
    names = tar.getnames()
    for name in names:
        tar.extract(name, path=saved_path)
    tar.close()

class Copy:
    def forceMergeFlatDir(self, srcDir, dstDir):
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
        for item in os.listdir(srcDir):
            srcFile = os.path.join(srcDir, item)
            dstFile = os.path.join(dstDir, item)
            self.forceCopyFile(srcFile, dstFile)

    def forceCopyFile (self, sfile, dfile):
        if os.path.isfile(sfile):
            shutil.copy2(sfile, dfile)

    def isAFlatDir(self, sDir):
        for item in os.listdir(sDir):
            sItem = os.path.join(sDir, item)
            if os.path.isdir(sItem):
                return False
        return True

    def copyTree(self, src, dst):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isfile(s):
                if not os.path.exists(dst):
                    os.makedirs(dst)
                self.forceCopyFile(s,d)
            if os.path.isdir(s):
                isRecursive = not self.isAFlatDir(s)
                if isRecursive:
                    self.copyTree(s, d)
                else:
                    self.forceMergeFlatDir(s, d)

class GithubAPI:
    def __init__(self, proxies=None):
        self.__basic_url = "https://api.github.com/"
        self.__proxies = proxies

    def __request_and_return(self, url):
        try:
            req = requests.get(url=url, verify=False, proxies=self.__proxies)
            if "message" in req.json().keys() \
                and req.json().get("message") == "Not Found":
                return False, "Not Found"
            return True, req.json()
        except Exception as error:
            return False, error

    def user_all_repos(self, username):
        # https://api.github.com/users/用户名/repos
        url = self.__basic_url + "users/" + username + "/repos"

        return self.__request_and_return(url=url)

    def repo_detail_info(self, username, repo_name):
        # https://api.github.com/repos/用户名/仓库名
        url = self.__basic_url + "repos/" + username + "/" + repo_name

        return self.__request_and_return(url=url)

    def repo_content_for_rootdir(self, solomonxie):
        # https://api.github.com/repositories/solomonxie/contents
        url = self.__basic_url + "repositories/" + \
            str(solomonxie) + "/contents"

        return self.__request_and_return(url=url)

    def repo_content_for_subdir(self, solomonxie, subdir):
        # https://api.github.com/repositories/solomonxie/contents/目录名
        url = self.__basic_url + "repositories/" + \
            str(solomonxie) + "/contents" + subdir

        return self.__request_and_return(url=url)

    def repo_file_detail(self, solomonxie, file_path):
        # https://api.github.com/repositories/solomonxie/gists/contents/文件路径
        url = self.__basic_url + "repositories/" + str(solomonxie) + \
            "/contents" + file_path

        return self.__request_and_return(url=url)

    def repo_file_raw(self, username, repo_name, branch, file_path):
        # https://raw.githubusercontent.com/用户名/仓库名/分支名/文件路径
        url = "https://raw.githubusercontent.com/" + \
            username + "/" + repo_name + "/" + branch + "/" + file_path

        return self.__request_and_return(url=url)

    def repo_commits_list(self, username, repo_name):
        # https://api.github.com/repos/用户名/仓库名/commits
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/commits"

        return self.__request_and_return(url=url)

    def repo_commit_detail(self, username, repo_name, sha):
        # https://api.github.com/repos/用户名/仓库名/commits/某一条commit的SHA
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/commits/" + sha

        return self.__request_and_return(url=url)

    def repo_issues_list(self, username, repo_name):
        # https://api.github.com/repos/用户名/仓库名/issues
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/issues"

        return self.__request_and_return(url=url)

    def repo_issue_detail(self, username, repo_name, number):
        # https://api.github.com/repos/用户名/仓库名/issues/序号
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/issues/" + str(number)

        return self.__request_and_return(url=url)

    def repo_issue_comments_list(self, username, repo_name, number):
        # https://api.github.com/repos/用户名/仓库名/issues/序号/comments
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/issues/" + str(number) + "/comments"

        return self.__request_and_return(url=url)

    def repo_issue_comment_detail(self, username, repo_name, comment_id):
        # https://api.github.com/repos/用户名/仓库名/issues/comments/评论详情的ID
        url = self.__basic_url + "repos/" + \
            username + "/" + repo_name + "/issues/comments/" + str(comment_id)

        return self.__request_and_return(url=url)

    def download_archive_file(self, username, repo_name, branch):
        # https://api.github.com/repos/用户名/仓库名/归档类型/分支名
        # https://github.com/用户名/仓库名/archive/分支名.tar.gz
        # 归档类型：tarball zipball
        url = "https://github.com/" + username + "/" + \
            repo_name + "/archive/" + \
            str(branch) + ".tar.gz"

        try:
            req = requests.get(url=url, verify=False)
            return True, req.content
        except Exception as error:
            return False, error

class PipExecutor:
    def __init__(self, origin=None):
        self.__origin = origin

    def __executor(self, arguments):
        FNULL = open(os.devnull, 'w')
        command = [sys.executable, "-m", "pip3", "-v"]
        try: # 检测pip版本
            subprocess.check_call(command, timeout=120, stdout=FNULL, stderr=subprocess.STDOUT)
            command = [sys.executable, "-m", "pip3"]
        except subprocess.CalledProcessError as error:
            command = [sys.executable, "-m", "pip"]

        command.extend(arguments)
        if self.__origin is not None:
            origin_list = ["-i", self.__origin]
            command.extend(origin_list)

        if command[3] in ["install", "uninstall"]:
            try:
                subprocess.check_call(command, timeout=120, stdout=FNULL, stderr=subprocess.STDOUT)
                return True, ""
            except subprocess.CalledProcessError as error:
                return False, error
        else:
            try:
                result = subprocess.check_output(command, timeout=120)

                if system_type() == "Windows":
                    return True, bytes.decode(result).split("\r\n")
                else:
                    return True, bytes.decode(result).split("\n")
            except subprocess.CalledProcessError as error:
                return False, error

    def install(self, package_list):
        arguments = ["install"]
        arguments.extend(package_list)
        ok, _ = self.__executor(arguments=arguments)

        if not ok:
            uninstalled_package_list = package_list
            ok, result = self.freeze()
            if ok:
                for i, package in enumerate(package_list):
                    for row in result:
                        if "==" not in package:
                            if package+"==" == row[:len(package+"==")]:
                                uninstalled_package_list.pop(i)
                        else:
                            if package == row[:len(package)]:
                                uninstalled_package_list.pop(i)

                return False, uninstalled_package_list
        else:
            return True, ""

    def uninstall(self, package_list):
        arguments = ["uninstall", "-y"]
        arguments.extend(package_list)
        ok, _ = self.__executor(arguments=arguments)
        if not ok:
            unremoved_package_list = []
            ok, result = self.freeze()
            if ok:
                for package in package_list:
                    for row in result:
                        print(package, row[:len(package)])
                        if "==" not in package:
                            if package+"==" == row[:len(package+"==")]:
                                unremoved_package_list.append(package)
                        else:
                            if package == row[:len(package)]:
                                unremoved_package_list.append(package)

                return False, unremoved_package_list
        else:
            return True, ""

    def show(self, package_name):
        arguments = ["show"]
        arguments.append(package_name)
        ok, result = self.__executor(arguments=arguments)

        return ok, result

    def search(self, package_name):
        arguments = ["search"]
        arguments.append(package_name)
        ok, result = self.__executor(arguments=arguments)

        return ok, result

    def freeze(self):
        arguments = ["freeze"]
        ok, result = self.__executor(arguments=arguments)

        return ok, result

    def list(self):
        arguments = ["list"]
        ok, result = self.__executor(arguments=arguments)

        return ok, result