import re
import textwrap
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup

from otkmodels.accounting import AccountTitle


계정과목_pattern = re.compile(r' *(([IVXⅠ-Ⅻ]+\.)|(\([0-9]+\))|([0-9]+\.)|([가-하]+\.))?(\(?[^\)]+\)?)')


def load_표준계정과목() -> Iterable[AccountTitle]:
    """
    법인세 전자신고 문서 중 4. 전자신고파일설명서(재무제표관련 계정과목코드)_20190214.doc 파일을 LibreOffice로 html로 저장한 다음 파싱한다.
    파싱 결과는 각 재무제표별로 계정과목 전체의 트리 구조를 AccountTitle에 담아서 yield한다.
    """
    with open(Path(__file__).parent / '4. 전자신고파일설명서(재무제표관련 계정과목코드)_20190214.html', encoding='utf8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

        for table in soup.find_all('table'):
            parents = []
            last_depth = 0
            depth = 0
            m = re.match(r'([^\(]+)(\([^\)0-9]+\))?[^\(]*\(([^\)]+)\)',
                         strip(table.find_previous_sibling('ol').text))

            분류 = strip(m.group(1))
            if m.group(2):
                분류 += '_' + m.group(2)[1:-1]

            root = prev = AccountTitle(name=분류, code=m.group(3), children=[])

            for tr in table.find_all('tr'):
                tds = tr.find_all('td')

                if not strip(tds[0].text).isnumeric():
                    continue

                if tds[1].find('strike'):
                    continue

                for strike in tds[2].find_all('strike'):
                    strike.extract()

                계정과목명 = strip(re.sub(r'\(((20[^\)]+)|(직접 ?기재))\)$', '', strip(tds[2].text)))

                match = 계정과목_pattern.match(계정과목명)
                if not match:
                    continue
                groups = match.groups()
                for i in range(1, 5):
                    if groups[i]:
                        depth = i
                        break

                if is_sub_account(groups[5]):
                    # if not is_sub_account(prev.계정과목명):
                    #     depth = last_depth + 1

                    order = ''
                else:
                    order = groups[depth]

                if '총계' in groups[5]:
                    depth = 1

                if last_depth < depth:
                    for j in range(last_depth, depth - 1):
                        parents.append(None)
                    parents.append(prev)
                elif last_depth > depth:
                    del parents[depth - last_depth:]

                last_depth = depth

                prev = AccountTitle(name=strip(groups[5]), code=strip(tds[1].text), old_code=strip(tds[0].text), seq=order or '', children=[])

                if [c for c in parents[-1].children if c.name == prev.name]:
                    continue

                if prev.name.startswith('('):
                    for child in reversed(parents[-1].children):
                        if not child.name.startswith('('):
                            parent = child
                            break
                    else:
                        raise Exception('Parent not found')
                else:
                    parent = parents[-1]

                parent.children.append(prev)
                prev.parent = parent

            yield root


def strip(text):
    return re.sub(r'\s+', ' ', text).strip().replace('· ', '·')


def is_sub_account(title):
    return title.startswith('(') and title.endswith(')')


if __name__ == '__main__':
    with open(Path(__file__).parent / '표준계정과목_법인세.py', 'w') as f:
        f.write(textwrap.dedent('''
            from otkmodels.accounting import AccountTitle
            
            
        '''))

        for root in load_표준계정과목():
            f.write(f'{root.name} = {{\n')
            for account in root.traverse():
                if account == root:
                    continue
                f.write(f'    "{account.path}": AccountTitle(name="{account.name}", code="{account.code}", old_code="{account.old_code}", seq="{account.seq}"),\n')
            f.write('}\n\n\n')
