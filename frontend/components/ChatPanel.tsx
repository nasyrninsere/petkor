"use client";

/**
 * 챗봇 패널 컴포넌트
 * - 메시지 입력/전송
 * - 말풍선 UI (사용자/AI 구분)
 * - 로딩, 에러 상태 처리
 * - 추천 장소 카드 임베디드 표시
 */
import { useState, useRef, useEffect, KeyboardEvent } from "react";
import type { ChatMessage, PlaceResult } from "@/lib/types";
import { sendChatMessage } from "@/lib/api";
import PlaceCard from "./PlaceCard";
import styles from "./ChatPanel.module.css";

interface ChatPanelProps {
  onPlacesUpdate: (places: PlaceResult[]) => void;
  onPlaceSelect: (contentId: string) => void;
}

const QUICK_PROMPTS = [
  "강릉에서 강아지랑 갈 수 있는 산책 장소",
  "제주 반려견 동반 카페 추천",
  "서울 강아지 공원 어디가 좋아요?",
  "부산에서 반려동물 동반 가능한 해수욕장",
];

export default function ChatPanel({ onPlacesUpdate, onPlaceSelect }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "안녕하세요! 🐾 저는 반려동물 동반여행 AI 어시스턴트예요.\n\n궁금한 지역이나 여행 스타일을 말씀해 주시면, 반려동물과 함께 갈 수 있는 최적의 여행지를 추천해 드릴게요!",
      places: [],
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 메시지 추가 시 스크롤
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (messageText?: string) => {
    const text = (messageText || input).trim();
    if (!text || isLoading) return;

    setInput("");
    setError(null);

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(text);

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        places: data.places,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // 지도 및 카드 리스트 업데이트
      if (data.places.length > 0) {
        onPlacesUpdate(data.places);
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.";
      setError(errMsg);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `❌ 오류가 발생했습니다: ${errMsg}\n\n잠시 후 다시 시도해 주세요.`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.panel}>
      {/* 헤더 */}
      <div className={styles.header}>
        <span className={styles.headerIcon}>🐾</span>
        <div>
          <div className={styles.headerTitle}>펫 트래블 AI</div>
          <div className={styles.headerSub}>반려동물 동반여행 전문 어시스턴트</div>
        </div>
        <div className={styles.statusDot} title="연결됨" />
      </div>

      {/* 메시지 목록 */}
      <div className={styles.messages}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.messageWrap} ${msg.role === "user" ? styles.userWrap : styles.assistantWrap} fade-in-up`}
          >
            {msg.role === "assistant" && (
              <div className={styles.avatar}>🤖</div>
            )}
            <div className={`${styles.bubble} ${msg.role === "user" ? styles.userBubble : styles.assistantBubble}`}>
              <div className={styles.bubbleText}>
                {msg.content.split("\n").map((line, i) => (
                  <span key={i}>
                    {line}
                    {i < msg.content.split("\n").length - 1 && <br />}
                  </span>
                ))}
              </div>

              {/* 추천 장소 카드 (AI 메시지에만) */}
              {msg.places && msg.places.length > 0 && (
                <div className={styles.placesInBubble}>
                  {msg.places.slice(0, 4).map((place) => (
                    <PlaceCard
                      key={place.contentId}
                      place={place}
                      compact
                      onClick={() => onPlaceSelect(place.contentId)}
                    />
                  ))}
                </div>
              )}

              <div className={styles.timestamp}>
                {msg.timestamp.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.messageWrap} ${styles.assistantWrap} fade-in-up`}>
            <div className={styles.avatar}>🤖</div>
            <div className={`${styles.bubble} ${styles.assistantBubble}`}>
              <div className={styles.typingDots}>
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 빠른 질문 버튼 */}
      {messages.length <= 1 && (
        <div className={styles.quickPrompts}>
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              className={styles.quickBtn}
              onClick={() => handleSend(prompt)}
              disabled={isLoading}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* 입력창 */}
      <div className={styles.inputArea}>
        <textarea
          ref={inputRef}
          id="chat-input"
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="예: 강릉에서 강아지랑 산책 가능한 곳 추천해줘"
          rows={2}
          disabled={isLoading}
          maxLength={500}
        />
        <button
          id="chat-send-btn"
          className={`btn-primary ${styles.sendBtn}`}
          onClick={() => handleSend()}
          disabled={isLoading || !input.trim()}
          aria-label="전송"
        >
          {isLoading ? <div className="spinner" /> : "전송"}
        </button>
      </div>
    </div>
  );
}
