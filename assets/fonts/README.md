# Bundled Pretendard

Pretendard Variable v1.3.9의 수정하지 않은 WOFF2 파일과 원본 라이선스다. 이력서와 포트폴리오 템플릿이 같은 파일을 사용한다. 전역 설치나 외부 CDN 요청은 필요하지 않다.

- [프로젝트](https://github.com/orioncactus/pretendard)
- [고정 버전 원본 폰트](https://github.com/orioncactus/pretendard/blob/v1.3.9/packages/pretendard/dist/web/variable/woff2/PretendardVariable.woff2)
- [원본 라이선스](https://github.com/orioncactus/pretendard/blob/v1.3.9/LICENSE), 로컬 사본: [LICENSE.txt](LICENSE.txt)
- 폰트 SHA-256: `9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4`

공유·이동 시 폰트와 라이선스를 함께 유지한다. `tools/prepare_documents.py`는 템플릿을 개인 출력 폴더에 복사하면서 폰트 파일·라이선스도 복사하고 상대 경로를 조정한다. HTML만 따로 이동하면 폰트 링크가 끊어질 수 있으므로 해당 출력 폴더 전체를 전달한다.

브라우저에서 로드 완료 후 PDF로 출력한다. 시스템 대체 글꼴로 표시된 결과를 Pretendard 출력으로 보고하지 않는다. 이 폰트는 토스 전용 서체나 TDS의 배포본이 아니다.
