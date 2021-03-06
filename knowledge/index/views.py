# -*- coding: utf-8 -*-

from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response, g
from flask.ext.security import login_required
import json
import csv
import os
import time
from datetime import date
from datetime import datetime
from get_result import *
from search_protrait import *
from knowledge.global_utils import graph
from GetUrl import getUrlByKeyWord,getUrlByKeyWordList
mod = Blueprint('index', __name__, url_prefix='/index')

@mod.route('/')
@login_required
def index():#首页

    user_name = g.user.email

    peo_infors = get_people(user_name,2)

    try:
        peo_string = 'START start_node=node:'+node_index_name+'("'+people_primary+':*") return count(start_node)'
        peo_object = graph.run(peo_string)

        for item in peo_object:
            peo_count = item['count(start_node)']
    except:
        peo_count = 0

    try:
        org_string = 'START start_node=node:'+org_index_name+'("'+org_primary+':*") return count(start_node)'
        org_object = graph.run(org_string)
        for item in org_object:
            org_count = item['count(start_node)']
    except:
        org_count = 0

    try:
        event_string = 'START start_node=node:'+event_index_name+'("'+event_primary+':*") return count(start_node)'
        event_object = graph.run(event_string)
        for item in event_object:
            event_count = item['count(start_node)']
    except:
        event_count = 0

    try:
        special_event_string = 'START start_node=node:'+special_event_index_name+'(\"'+special_event_primary+':*") return count(start_node)'
        special_event_object = graph.run(special_event_string)
        for item in special_event_object:
            special_event_count = item['count(start_node)']
    except:
        special_event_count = 0

    try:
        group_string = 'START start_node=node:'+group_index_name+'("'+group_primary+':*") return count(start_node)'
        group_object = graph.run(group_string)
        for item in group_object:
            group_count = item['count(start_node)']
    except:
        group_count = 0

    neo_count = {'people':peo_count, 'org':org_count, 'event':event_count, 'special_event':special_event_count, 'group':group_count}
    
    weibo_list = get_hot_weibo()

    people_list = get_hot_people()    
    
    return render_template('index/knowledge_home.html', peo_infors = peo_infors, neo_count = neo_count, weibo_list = weibo_list,\
                           people_list = people_list)

@mod.route('/get_index_map/')
def get_index_map():#地图

    map_count = get_map_count()

    return json.dumps(map_count)

@mod.route('/graph/', methods=['GET','POST'])
@login_required
def get_graph():#图谱页面

    user_id = request.args.get('user_id', '')
    node_type = request.args.get('node_type', '')

    if node_type == 'ALL':#首页跳转
        relation = get_all_graph()
        flag = 'Success'
    elif node_type == 'people':#人物节点图谱
        relation = get_people_graph(user_id)
        flag = 'Success'
    elif node_type == 'event':#事件节点图谱
        relation = get_event_graph(user_id)
        flag = 'Success'
    elif node_type == 'org':#机构节点图谱
        relation = get_org_graph(user_id)
        flag = 'Success'
    elif node_type == 'topic':#专题节点图谱
        relation = get_special_event_graph(user_id)
        flag = 'Success'
    elif node_type == 'group':#群体节点图谱
        relation = get_group_graph(user_id)
        flag = 'Success'
    else:
        relation = []
        flag = 'Wrong Type'

    return render_template('index/knowledgeGraph.html', relation = relation, flag = flag)

@mod.route('/map/', methods=['GET','POST'])
@login_required
def get_map():#地图页面

    user_id = request.args.get('user_id', '')
    node_type = request.args.get('node_type', '')

    if node_type == 'ALL':#首页跳转
        event_result,people_result,org_relation = get_all_geo()
        flag = 'Success'
    elif node_type == 'people':#人物节点图谱
        event_result,people_result,org_relation = get_people_geo(user_id)
        flag = 'Success'
    elif node_type == 'event':#事件节点图谱
        event_result,people_result,org_relation = get_event_geo(user_id)
        flag = 'Success'
    elif node_type == 'org':#机构节点图谱
        event_result,people_result,org_relation = get_org_geo(user_id)
        flag = 'Success'
    elif node_type == 'topic':#专题节点图谱
        event_result,people_result,org_relation = get_topic_geo(user_id)
        flag = 'Success'
    elif node_type == 'group':#群体节点图谱
        event_result,people_result,org_relation = get_group_geo(user_id)
        flag = 'Success'
    else:
        event_result = []
        people_result = []
        org_relation = []
        flag = 'Wrong Type'

    data_dict = {'event':event_result,'people':people_result,'org':org_relation}
    return render_template('index/baidu_map.html', data_dict = data_dict, flag = flag)

@mod.route('/person/', methods=['GET','POST'])
@login_required
def get_person_atr():#人物属性页面

    user_id = request.args.get('user_id', '')

    ### 人物属性查询函数
    if user_id:
        result_att = search_person_by_id(user_id)
    else:
        result_att = {}

    ### 获取相关wiki
    try:
        if result_att['uname']:#name不为空
            wiki_list = getUrlByKeyWord(result_att['uname'])
        else:
            wiki_list = []
    except KeyError:
        wiki_list = []

    ### 获取关联实体
    if user_id:
        relation_dict = search_neo4j_by_uid(user_id,node_index_name,people_primary)
    else:
        relation_dict = {'people':[],'org':[],'event':[]}
    
    relation_dict['wiki'] = wiki_list[0:10]

    return render_template('index/person.html',result_att = result_att,relation_dict = relation_dict)

@mod.route('/event/', methods=['GET','POST'])
@login_required
def get_event_atr():#事件属性页面

    user_id = request.args.get('user_id', '')

    ### 事件属性查询函数
    if user_id:
        result_att = search_event_by_id(user_id)
    else:
        result_att = {}

    ### 获取相关wiki
    try:
        if result_att['name']:#name不为空
            key_words = result_att['name'].split('&') 
            wiki_list = getUrlByKeyWordList(key_words)
        else:
            wiki_list = []
    except KeyError:
        wiki_list = []

    ### 获取关联实体
    if user_id:
        relation_dict = search_neo4j_by_uid(user_id,event_index_name,event_primary)
    else:
        relation_dict = {'people':[],'org':[],'event':[]}
    
    relation_dict['wiki'] = wiki_list[0:10]
    
    return render_template('index/event.html',result_att = result_att,relation_dict = relation_dict)

@mod.route('/organization/', methods=['GET','POST'])
@login_required
def get_organization():#机构属性页面

    user_id = request.args.get('user_id', '')

    ### 机构属性查询函数
    if user_id:
        result_att = search_org_by_id(user_id)
    else:
        result_att = {}

    ### 获取相关wiki
    try:
        if result_att['uname']:#name不为空
            wiki_list = getUrlByKeyWord(result_att['uname'])
        else:
            wiki_list = []
    except KeyError:
        wiki_list = []

    ### 获取关联实体
    if user_id:
        relation_dict = search_neo4j_by_uid(user_id,org_index_name,org_primary)
    else:
        relation_dict = {'people':[],'org':[],'event':[]}
    
    relation_dict['wiki'] = wiki_list[0:10]
    
    return render_template('index/organization.html',result_att = result_att,relation_dict = relation_dict)

@mod.route('/cards/', methods=['GET','POST'])
@login_required
def get_card():#卡片罗列页面

    user_id = request.args.get('user_id', '')
    node_type = request.args.get('node_type', '')
    card_type = request.args.get('card_type', '')
    user_name = g.user.email

    result,flag = get_relation_node(user_id,node_type,card_type,user_name)#获取关联节点

    return render_template('index/card_display.html', result = result, flag = flag)

@mod.route('/show_attention/', methods=['GET','POST'])
def show_attention():

    user_name = request.form['user_name']
    s_type = request.form['s_type']
    
    if s_type == 'people':
        infors = get_people(user_name,2)
    elif s_type == 'event':
        infors = get_event(user_name,2)
    else:
        infors = get_org(user_name,2)

    return json.dumps(infors)

### for neo4j test
@mod.route('/test/')
def neo4j_test():

    p_string = 'START n=node:event_index(event_id="bei-jing-fang-jia-zheng-ce-1480176000") return labels(n)'
    p_result = graph.run(p_string)
    for item in p_result:
        print item

    return 'sss'

@mod.route('/wiki/')
def wikitest():
    key = "特朗普"
    wiki_list = getUrlByKeyWord(key)
    return json.dumps(wiki_list)

    
