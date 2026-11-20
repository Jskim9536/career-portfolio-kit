# A4 HTML → 한·영 PDF

## 레이아웃

제공된 이력서의 텍스트 중심 위계를 일반화했다. 이름·직무·연락처, 얇은 선으로 구분한 섹션, 왼쪽 기관·역할과 오른쪽 기간, 간결한 불릿을 사용한다. 개인 이력이나 로컬 자산은 포함하지 않는다.

템플릿은 한·영 각각 A4 1쪽이다. 학생은 프로젝트 중심으로, 경력자는 관련 경력 중심으로 교체한다. 2쪽이 필요하면 `.page` 블록을 복사해 내용을 나누고 페이지 번호를 갱신한다. 이어지는 경력에는 기관·역할과 `계속 / continued`를 표시한다. 한 항목을 가능하면 함께 두되 큰 공백이 생기면 명시적으로 나눈다.

- `@page { size: A4; margin: 0; }`, `.page`는 210×297mm.
- `.page-content` 안에 본문을 넣고 별도 푸터 영역을 확보한다. 내용이 길어져도 숨기지 않는다. 인쇄 전 본문 높이가 영역을 넘는지 확인하고 항목을 다음 페이지로 옮긴다.
- 이름 23pt, 직무 11pt, 섹션 약 11pt, 본문 10pt·줄간격 1.45, 보조 정보 9pt를 시작점으로 삼는다. 크기를 줄여 페이지 수를 맞추기보다 내용을 편집한다.
- 본문 흐름은 한 열. 핵심 역량만 짧은 3열 요약으로 쓸 수 있다. 장식용 그래프·숙련도 막대·사진·아이콘은 기본으로 넣지 않는다.
- `lang="ko"` 또는 `lang="en"`, 실제 문서 제목, 선택 가능한 텍스트, `a href` 링크를 유지한다. 긴 URL 대신 `GitHub`, `Portfolio` 같은 짧은 라벨을 사용한다. 예시용 링크를 실제 링크처럼 제출하지 않는다.
- Pretendard가 있으면 사용하고, 없으면 Noto Sans KR·맑은 고딕 등 실제 설치된 한글 지원 폰트로 대체한다. 외부 웹 폰트가 필요하면 로드 완료 후 출력하고 대체 여부를 확인한다.
- 화면에서는 가로 스크롤을 허용하되 A4 내부를 반응형으로 재배치하지 않는다. 인쇄 때 화면 배경·그림자를 제거한다.

## 두 언어를 각각 출력

아래 명령은 저장소 루트 기준이다. 출력 폴더는 예시이며 실제 지원서는 개인 작업 공간에 둔다.

```bash
python3 tools/export_pdf.py output/resume-ko.html output/resume-ko.pdf
python3 tools/export_pdf.py output/resume-en.html output/resume-en.pdf
python3 tools/check_pdf.py output/resume-ko.pdf --kind resume
python3 tools/check_pdf.py output/resume-en.pdf --kind resume
```

이 검사기는 `pypdf`가 필요하다. 브라우저는 Chrome·Chromium·Edge 중 설치된 것을 사용하며 필요하면 `--browser`로 경로를 지정한다. 자동 전역 설치를 전제하지 않는다. 기존 파일 교체는 의도한 경우에만 `--overwrite`로 수행한다.

브라우저 수동 출력은 A4 세로, 배율 100%, 여백 없음, 머리글·바닥글 없음, 배경 그래픽 포함으로 설정한다. 출력한 PDF를 실제로 다시 확인한다. 코드만 제공하고 PDF도 생성했다고 말하지 않는다.

검사 옵션 예시:

```bash
python3 tools/check_pdf.py output/resume-ko.pdf --kind resume --require-text '실제 지원자 이름' --require-uri 'https://실제-근거-링크'
python3 tools/check_pdf.py output/resume-en.pdf --kind resume --max-pages 3
```

`--max-pages`는 제출 조건상 2쪽을 넘겨야 할 때만 설정한다. 자동 검사는 A4 세로·페이지 한도·텍스트 존재·지정한 링크/문구를 확인하며 내용의 사실성이나 시각적 완성도를 보장하지 않는다.

## 최종 확인

`pdftoppm -r 150 -png output/resume-ko.pdf work/resume-ko` 등으로 **한·영 PDF의 모든 페이지**를 렌더링해 글리프·줄바꿈·여백·잘림·푸터를 확인한다. 한글 추출, 영문 특수문자, 굵기와 PDF 폰트 포함 상태도 점검한다. 회사가 순수 텍스트나 특정 ATS 형식을 요구하면 복사·추출 순서를 확인하고 해당 양식을 우선한다. 어떤 PDF도 모든 ATS에서 정상 파싱된다고 보장하지 않는다.

수정 후 해당 HTML에서 PDF를 다시 출력하고 최종 4개 파일의 버전을 맞춘다. 파일명·HTML title·PDF 제목·푸터에 이전 회사나 지원 직무가 남지 않았는지 대조한다.
