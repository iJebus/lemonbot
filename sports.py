#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import arrow
import re
import requests

from bs4 import BeautifulSoup


BASE = 'http://app.sportdata.com.au'
ORGS = {
    'lords': '/find_sports/91'
}
STATS_TH = ['Team', 'Pos', 'Points', '%', 'For', 'Ag', 'Play', 'Won', 'Lost',
            'Draw', 'Bye', 'FW', 'FL', 'B']
TIMES_TH = ['Round', 'Game Date', 'Team A', 'Team B', 'A', 'B', 'F']


def create_session(org):
    """Why do this and not just scrape the whole thing?"""
    session = requests.Session()
    session.get(BASE + ORGS[org])
    return session


def search_team_name(session, name):
    payload = {'term': name}
    r = session.get(BASE + '/autocomplete/leagues', params=payload)
    return [parse_team(x) for x in r.json()]


def parse_team(team):
    session, division, name = team['label'].split(' - ')
    return {
        'session': session,
        'division': division,
        'name': name,
        'id': str(team['id'])
    }


def parse_results_page(html, team):
    bs = BeautifulSoup(html, 'html.parser')
    bs_results = bs.find('div', {'id': 'results'})
    bs_tables = bs_results.find_all('table')
    stats = parse_team_stats(bs_tables[0], team)
    times = parse_game_times(bs_tables[1], team)
    return (stats, times)


def parse_team_stats(bs_standings_table, team):
    td = bs_standings_table.find('td', text=re.compile(team))
    stats = list(td.parent.stripped_strings)
    return dict(zip(STATS_TH, stats))


def parse_game_times(bs_times_table, team):
    tds = bs_times_table.find_all('td', text=re.compile(team))
    td_family = [list(x.parent.stripped_strings) for x in tds]
    return [x[1] for x in td_family if 'bye' not in x]


def load_results_page(session, id):
    payload = {'team_id': id}
    r = session.get(BASE + '/find_team', params=payload)
    return r.text


def next_game(times):
    try:
        now = arrow.utcnow()
        arrow_times = [arrow.get(x, 'D MMMM YYYY') for x in times]
        future_times = [x for x in arrow_times if x > now]
        return future_times[0]
    except IndexError as e:
        return


if __name__ == "__main__":
    s = create_session('lords')
    possible_teams = search_team_name(s, 'Net-tricks')
    team = possible_teams[0]
    results_page = load_results_page(s, team['id'])

    stats, times = parse_results_page(results_page, team['name'])
    print(next_game(times))
    # [x.text for x in bs_results.find_all('th')]
    # [x.text for x in bs_results_team[0].parent.find_all('td')]
    # print(list(soup_results.find_all(
    # 'td', text=re.compile('^Net'))[1].parent.children)[3].text.strip())
