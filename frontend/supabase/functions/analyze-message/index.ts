import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// 기본 응답 구조 (프론트엔드가 기대하는 모든 필드 보장)
function createDefaultResult(message: string, isError = false) {
  return {
    isScam: false,
    riskLevel: "보통",
    riskScore: 50,
    scamType: isError ? "분석 오류" : "분석 불가",
    confidence: 0,
    riskFactors: isError 
      ? ["분석 중 오류가 발생했습니다. 다시 시도해주세요."] 
      : ["AI 분석 결과를 파싱할 수 없습니다"],
    analysis: message,
    patternsCount: 0,
    casesCount: 0,
    processingTime: "0초",
  };
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  const startTime = Date.now();

  try {
    const { message, sender } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
      const result = createDefaultResult("API 키가 설정되지 않았습니다.", true);
      return new Response(JSON.stringify(result), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (!message || typeof message !== "string" || message.trim().length < 2) {
      const result = createDefaultResult("분석할 메시지를 입력해주세요.", true);
      return new Response(JSON.stringify(result), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    console.log("Analyzing message:", message.substring(0, 50) + "...");
    console.log("Sender:", sender || "Unknown");

    const startTime = Date.now();

    const systemPrompt = `당신은 한국의 사기 메시지를 분석하는 전문 AI입니다. 
보이스피싱, 스미싱, 대출 사기, 로맨스 스캠, 투자 사기 등 다양한 사기 유형을 탐지합니다.

분석 시 다음 사항을 고려하세요:
1. 긴급성을 강조하는 표현 (급히, 지금 바로, 즉시 등)
2. 금전적 요구 (이체, 송금, 입금, 계좌 등)
3. 공공기관 사칭 (금융감독원, 검찰, 경찰, 은행 등)
4. 개인정보 요구 (비밀번호, 주민번호, 계좌번호 등)
5. 비정상적인 연락처 (해외번호, 일반 휴대폰으로 공공기관 사칭)
6. 너무 좋은 조건 (저금리 대출, 당일 대출, 수수료 없음 등)
7. 링크 클릭 유도
8. 문법/맞춤법 오류

반드시 다음 JSON 형식으로만 응답하세요:
{
  "isScam": boolean,
  "riskLevel": "매우높음" | "높음" | "보통" | "낮음",
  "riskScore": number (0-100),
  "scamType": string,
  "confidence": number (0-100),
  "riskFactors": string[],
  "analysis": string,
  "patternsCount": number,
  "casesCount": number
}`;

    const userPrompt = `다음 메시지를 분석해주세요:

메시지: "${message}"
${sender ? `발신자: ${sender}` : ''}

위의 메시지가 사기인지 분석하고, JSON 형식으로 결과를 반환해주세요.`;

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "요청이 너무 많습니다. 잠시 후 다시 시도해주세요." }), {
          status: 200,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (response.status === 402) {
        return new Response(JSON.stringify({ error: "서비스 이용 한도를 초과했습니다." }), {
          status: 200,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const errorText = await response.text();
      console.error("AI gateway error:", response.status, errorText);
      throw new Error(`AI gateway error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content;
    
    console.log("AI Response:", content);

    // Parse JSON from response
    let result;
    try {
      // Extract JSON from response (in case there's extra text)
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        result = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error("No JSON found in response");
      }
    } catch (parseError) {
      console.error("Failed to parse AI response:", parseError);
      // Return a fallback analysis
      result = {
        isScam: false,
        riskLevel: "보통",
        riskScore: 50,
        scamType: "분석 불가",
        confidence: 50,
        riskFactors: ["AI 분석 결과를 파싱할 수 없습니다"],
        analysis: content || "분석을 완료할 수 없습니다.",
        patternsCount: 0,
        casesCount: 0
      };
    }

    const processingTime = ((Date.now() - startTime) / 1000).toFixed(1) + "초";
    result.processingTime = processingTime;

    console.log("Analysis complete:", result.riskLevel, "Risk Score:", result.riskScore);

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in analyze-message function:", error);
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : "분석 중 오류가 발생했습니다." 
    }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
