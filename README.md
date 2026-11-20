# Career Portfolio Kit

대학생의 커리어 준비를 돕는 공용 AI 스킬과 템플릿입니다. GitHub·README 정리, HTML 기반 PDF 포트폴리오, A4 학술 포스터 초안을 실제 프로젝트 근거로 작성합니다.

## 필요한 스킬 선택

| 하고 싶은 일 | 스킬 | 결과 |
|---|---|---|
| 프로젝트와 본인 기여를 정리하고 첨삭받기 | [student-project-portfolio](skills/student-project-portfolio/SKILL.md) | 프로젝트 설명·README·보완 과제 |
| HTML로 포트폴리오를 만들고 PDF로 출력하기 | [html-pdf-portfolio](skills/html-pdf-portfolio/SKILL.md) | 편집 HTML + 10페이지 이내 PDF |
| 학회 발표 형태의 A4 포스터 만들기 | [academic-a4-poster](skills/academic-a4-poster/SKILL.md) | 편집 HTML + A4 1페이지 PDF 초안 |

포스터 스킬은 Behance의 학술 포스터·타이포그래피 사례와 대학 도서관의 디자인 가이드를 참고했습니다. [레퍼런스와 확인 범위](skills/academic-a4-poster/references/design-and-references.md)를 기록했으며, 타인의 원본 이미지나 유료 템플릿은 포함하지 않습니다.

## 시작하기

1. GitHub의 **Code → Download ZIP** 또는 아래 명령으로 받습니다.

   ```bash
   git clone https://github.com/Jskim9536/career-portfolio-kit.git
   ```

2. 파일을 읽고 편집할 수 있는 AI 도구에서 폴더를 열고, [시작 문구](START-HERE.md)를 전달합니다. 채팅만 사용하는 경우 해당 `SKILL.md`와 연결된 참고 문서·HTML 템플릿을 첨부합니다. 도구에 따라 ZIP 해제나 파일 생성 기능이 다를 수 있습니다.
3. 코드·README·화면·실험 로그 등 본인 자료를 제공합니다. 공개할 수 없는 자료는 이 저장소에 올리지 않고 개인 작업 공간에서 사용합니다.
4. AI가 자료를 읽고 부족한 사실을 질문하면 답합니다. 없는 수치와 결과를 만들지 않습니다.
5. HTML을 브라우저에서 열고 수정한 뒤 PDF로 저장합니다. 출력 PDF도 다시 확인합니다.

이 저장소를 받는 것만으로 전역 스킬이 설치되지는 않습니다. 설치 없이 파일의 지침을 읽도록 요청해 사용할 수 있습니다.

## 템플릿과 예시

- [프로젝트 전체 목록](templates/PROJECT-INVENTORY.md): 모든 경험을 빠짐없이 연결합니다.
- [학생 사전 질문지](templates/STUDENT-INTAKE.md), [프로젝트 README](templates/PROJECT-README.md).
- [포트폴리오 HTML](skills/html-pdf-portfolio/assets/portfolio.html): 8페이지 시작 템플릿. 내용에 따라 최대 10페이지로 조정합니다.
- [A4 포스터 HTML](skills/academic-a4-poster/assets/poster.html): 2열 구조의 학술형 초안.
- [템플릿 PDF 예시](examples/): 실제 학생 실적이 아닌 구조·출력 확인용입니다.
- [미니 실험 가이드](MINI-PROJECTS.md): 설명할 경험이 부족할 때의 작은 보완 과제입니다. 실제 코드 실행과 환경 준비가 별도로 필요합니다.

전체 프로젝트는 GitHub 목록에 정리하고, PDF와 포스터에는 대표 사례를 선별합니다. A4 포스터는 초안 규격이며 대형 출력은 행사 규격에 맞춰 별도로 조판합니다.

## PDF 출력

가장 간단한 방법은 브라우저의 **인쇄 → PDF 저장**입니다. 배경 그래픽을 포함하고 머리글·바닥글을 끕니다. 포트폴리오는 HTML의 16:9 사용자 지정 크기, 포스터는 A4인지 확인합니다.

Python과 Chrome·Chromium·Edge가 있다면 자동 출력도 가능합니다. 자동 설치는 하지 않습니다.

```bash
python3 tools/export_pdf.py skills/academic-a4-poster/assets/poster.html output/poster.pdf
python3 tools/export_pdf.py skills/html-pdf-portfolio/assets/portfolio.html output/portfolio.pdf
```

Windows에서는 설치 환경에 따라 `python3` 대신 `python` 또는 `py`를 사용합니다. 브라우저를 찾지 못하면 `--browser`로 실행 파일 경로를 지정합니다. 기존 결과를 덮어쓸 때만 `--overwrite`를 사용합니다. 외부 웹 폰트·이미지가 있는 문서는 로드 상태를 별도로 확인하세요.

`pypdf`가 있는 Python 환경에서는 다음으로 페이지 수·규격·텍스트·링크 주석을 확인할 수 있습니다. 검사가 통과해도 모든 페이지의 시각 검토가 필요합니다.

```bash
python3 tools/check_pdf.py output/poster.pdf --kind poster
python3 tools/check_pdf.py output/portfolio.pdf --kind portfolio
```

## 공개 자료의 범위

이 저장소에는 공용 지침·빈 템플릿·안내용 예시를 둡니다. 학생 이력서·연락처·비공개 코드·개별 피드백은 개인 저장소나 허가된 공간에서 관리합니다. 타인의 코드·데이터·그림을 사용하면 원본 출처와 해당 라이선스를 확인합니다.

완성된 학생 포트폴리오의 사실 확인은 본인과 멘토가 수행해야 합니다. 자동 검사 결과와 실제 확인 범위는 [검증 기록](VALIDATION.md)에 남깁니다.
