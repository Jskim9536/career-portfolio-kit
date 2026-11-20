# 채점·판정·보고서

## 수준 0~4

| 수준 | 관찰 가능한 상태 |
|---|---|
| 0 | 문서상 증거 없음, 요건과 무관, 또는 정본과 모순되는 주장 |
| 1 | 핵심어·일반 주장만 있고 수행 범위·근거가 드러나지 않음 |
| 2 | 인접·부분 경험 또는 구체성이 일부 부족한 직접 경험. 미충족 부분 설명 필요 |
| 3 | 직접 관련 경험과 본인 역할·행동·산출물이 명확하고 해당 문서의 기본 인수조건 충족 |
| 4 | 수준 3에 더해 선택·조건·검증·결과가 인수조건에 맞게 충분히 드러남 |

수치만 있어야 수준 4가 되는 것은 아니다. 직무에 맞는 실제 산출물·시험·운영 근거도 가능하다. 서술과 정본의 일치가 필요하며, 멋진 문구나 같은 핵심어 반복은 가점하지 않는다. JD에 없는 양산·논문·최신 모델을 일괄 요구하지 않는다. `min_level`은 항목별 목표 수준이며 우대항목의 미달 자체가 필수 자격 탈락이 되지는 않는다.

문서별 점수 = `100 × Σ(weight × level / 4) / Σ(적용되는 weight)`. 각 항목에서 resume/portfolio에 다른 인수조건을 적용하고, 언어 버전은 따로 채점한다. 여러 문서의 요약 점수는 **최저 문서 점수**를 사용하며 평균으로 약한 문서를 숨기지 않는다.

## 품질 게이트

각 게이트는 `status`, `reason`, `evidence`로 기록한다. evidence에는 검사한 파일·위치·정본 참조와 실제 확인 범위를 남긴다. 민감정보 원문을 복사하지 않는다.

| 게이트 ID | pass에 필요한 확인 |
|---|---|
| facts | 이름·학력·기간·직함·역할·수치·단위·실측/목표가 제공 정본과 일치, 문서 간 모순 없음 |
| privacy | 불필요한 개인정보·제3자 정보·인증정보·미승인 회사 기밀 제거 또는 적법한 공개 범위 확인 |
| editorial | 한국어 맞춤법·띄어쓰기·명사형, 영어 문법·시제·자연스러움, 숫자·약어 표기 검수 |
| language_parity | 한·영 버전의 사실·기여·성과·상태 일치. 단일 언어만 대상이면 `na` 가능 |
| target_identity | 회사·직무·이름·버전이 파일명·본문·title·PDF 메타데이터·푸터에서 일치 |
| rendering | 대상 형식 전부 생성, HTML·PDF 내용 일치, 모든 페이지 시각 검수·규격·글자·링크 확인 |
| submission | JD의 파일 형식·분량·언어·파일 크기 등 명시 제출 조건 충족. 미지정이면 키트 기본값 확인 |

`pass / fail / unknown`을 사용하고 `na`는 단일 언어의 language_parity에만 허용한다. 원본 자료·PDF·공개 승인에 접근하지 못했다면 해당 검사는 unknown으로 남긴다. 이름·지원자 연락용 이메일 등 승인된 기본 연락처는 무조건 삭제하지 않는다. 이 검수는 법적 적법성이나 정보 유출 부재를 보장하는 감사가 아니다.

## 자체 인수조건과 판정

기본은 모든 문서 점수 ≥80, 문서별 must_have·responsibilities 정규화 점수 각각 ≥75, 모든 품질 게이트 pass(허용된 na 제외), 모든 critical 자격 pass 및 적용 문서의 critical 항목 min_level 충족이다. critical 항목은 직접 근거가 필요한 수준 3 이상으로 설정한다. 기준 수립 시 사용자 조건에 맞춰 수치 기준을 바꾸고 고정할 수 있다.

- **ACCEPT:** 자체 인수조건 충족. 실제 합격 예측이나 지원 완료 의미 아님.
- **REVISE:** 문장·배치·번역·사실 오류·노출·출력 문제 또는 점수 부족이 있어 수정 필요.
- **NEEDS_EVIDENCE:** 핵심 사실·자격·공개 범위·검사 결과가 unknown. 영향 없는 수정은 완료하고 필요한 자료를 구체적으로 요청.
- **FIT_GAP:** 명시된 critical 자격이 근거상 fail. 표현 수정으로 해소할 수 없음. 다른 문제와 수정 파일도 함께 전달.

문서 자체의 `artifact_ready`와 자격 포함 `acceptance_met`를 별도로 기록한다. 내용·출력 검수는 끝났어도 실제 자격이 부족하면 후자는 false다. 실제 경험 격차를 숨겨 ACCEPT로 만들거나 사용자의 지원 의사를 대신 판단하지 않는다.

## 리뷰 JSON 계약

`review-before.json`, `review-after.json`은 아래 구조다. 예시는 축약이며 실제 파일은 계획에 포함된 모든 문서·평가 항목·게이트·critical 자격을 빠짐없이 포함한다. JSON에서 파일 경로는 **리뷰 JSON이 있는 폴더 기준**이며 해시는 실제 파일 바이트의 SHA-256이다. 계산기는 해시·범위·누락·산식을 검증한다. PDF가 아직 없으면 artifacts에 HTML만 두고 rendering은 unknown 또는 fail로 남긴다.

```json
{
  "schema_version": 1,
  "criteria_id": "application-jd-v1",
  "criteria_sha256": "criteria.json 파일 바이트의 실제 SHA-256",
  "documents": [
    {
      "id": "resume-ko",
      "artifacts": [
        {"format": "html", "path": "../v1/resume-ko.html", "sha256": "실제 파일 해시"},
        {"format": "pdf", "path": "../v1/resume-ko.pdf", "sha256": "실제 파일 해시"}
      ]
    }
  ],
  "ratings": [
    {
      "document_id": "resume-ko",
      "criterion_id": "M1",
      "level": 2,
      "reason": "모듈 구현은 설명됐으나 본인 수정 범위가 불명확",
      "document_evidence": ["resume-ko.html 프로젝트 1, 두 번째 불릿"],
      "source_evidence": ["본인 프로젝트 README 기여 항목"]
    }
  ],
  "critical_requirements": [],
  "gates": {
    "facts": {"status": "pass", "reason": "제공 정본과 대조", "evidence": ["근거표 F1~F8"]},
    "privacy": {"status": "pass", "reason": "실제 검사 범위 설명", "evidence": ["검사 파일·이미지·링크 목록"]},
    "editorial": {"status": "pass", "reason": "언어별 교정 완료", "evidence": ["검사 문서·페이지"]},
    "language_parity": {"status": "pass", "reason": "수치·역할·기간 대조", "evidence": ["한영 대조표"]},
    "target_identity": {"status": "pass", "reason": "대상 정보 대조", "evidence": ["파일명·title·푸터·메타데이터"]},
    "rendering": {"status": "unknown", "reason": "PDF 시각 검수 전", "evidence": ["아직 확인하지 못한 페이지 목록"]},
    "submission": {"status": "pass", "reason": "명시 제출 조건 대조", "evidence": ["JD 제출 조건과 출력 목록"]}
  }
}
```

critical 항목마다 `{"criterion_id":"M2","status":"pass|fail|unknown","reason":"근거 설명","evidence":["정본 위치"]}`를 포함한다. 문서에 내용이 없으면 level 0과 확인한 문서 위치를 적는다. 정본 자체가 없으면 그 사실을 source_evidence에 적고 facts는 unknown으로 둔다. 검사하지 않은 항목을 pass로 채우지 않는다.

## 읽기 쉬운 보고서

`review.md`와 `revision-log.md`에는 다음을 남긴다.

1. 기준 ID·JD·대상 문서 버전·점수의 의미·검사 범위.
2. 문서별 점수와 category별 점수, critical 자격 상태, 게이트 판정.
3. 상위 수정 3~5개: 항목 ID·파일/페이지/요소·문제·원인·정본·구체적 수정·완료 기준.
4. 문장 예시의 기존/수정 비교. 민감정보는 `[REDACTED]` 등으로 가리고 실제 비밀을 로그에 복제하지 않음.
5. 재채점: 항목별 이전→이후, 변경된 근거, 해결·보류·실제 경험 부족의 구분.
6. 남은 자료 요청과 아직 수행하지 못한 검사. 점수가 올라가지 않았어도 실제 결과대로 기록.

직접 제공된 JD/평가표가 아니라면 `자체 문서 평가 기준`이라고 표시한다. 통계적 검증 없이 합격률·서류 통과율·확률의 숫자를 만들지 않는다.
