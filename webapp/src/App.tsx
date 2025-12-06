import { useEffect } from "react";

const SECTIONS = [
  { id: "shop", title: "🏪 Магазин", description: "Купить оборудование Thule" },
  { id: "rental", title: "🚗 Аренда", description: "Арендовать бокс или багажник" },
  { id: "market", title: "📦 Рынок", description: "Продать или купить б/у оборудование" },
  { id: "repair", title: "🧰 Ремонт", description: "Заявка на ремонт оборудования" },
  { id: "faq", title: "❓ FAQ", description: "Ответы на частые вопросы" },
  { id: "community", title: "💬 Сообщество", description: "Обсуждение и чат" },
];

const ADMIN_ID = 230325201;

function App() {
  const tg = window.Telegram?.WebApp;
  const user = tg?.initDataUnsafe?.user;
  const isAdmin = user && user.id === ADMIN_ID;

  useEffect(() => {
    tg?.ready();
    tg?.expand();
  }, [tg]);

  const handleClick = (sectionId: string) => {
    tg?.sendData(JSON.stringify({ type: "open_section", section: sectionId }));
  };

  // Генерация случайной позиции и наклона бетонного блока
  const randomParams = () => {
    return {
      rot: Math.floor(Math.random() * 6 - 3),
      offsetX: Math.floor(Math.random() * 10 - 5),
      offsetY: Math.floor(Math.random() * 10 - 5),
    };
  };

  // Эффект пыли при падении
  const createDust = (element: HTMLElement) => {
    const dust = document.createElement("div");

    Object.assign(dust.style, {
      position: "absolute",
      width: "90px",
      height: "90px",
      backgroundImage: "url('/thule_hub_bot/images/dust.png')",
      backgroundSize: "cover",
      pointerEvents: "none",
      opacity: "0",
      bottom: "-25px",
      left: "50%",
      transform: "translateX(-50%) scale(0.5)",
      animation: "dustFade 0.85s ease-out forwards",
    });

    element.appendChild(dust);

    setTimeout(() => dust.remove(), 900);
  };

  return (
    <div
      style={{
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        minHeight: "100vh",
        color: "#fff",
        background: "transparent",
        position: "relative",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          fontSize: "26px",
          fontWeight: "700",
          marginBottom: "10px",
          color: "#4CAF50",
          textShadow: "0 3px 6px rgba(0,0,0,0.7)",
        }}
      >
        Thule Hub Russia
      </h1>

      {/* MAIN BUTTONS */}
      {SECTIONS.map((section, index) => {
        const { rot, offsetX, offsetY } = randomParams();

        return (
          <div
            key={section.id}
            onClick={() => handleClick(section.id)}
            ref={(el) => {
              if (el) {
                setTimeout(() => createDust(el), index * 140 + 350); // пыль появляется после падения
              }
            }}
            style={{
              position: "relative",
              padding: "20px",
              borderRadius: "12px",

              // бетон
              backgroundImage: "url('/thule_hub_bot/images/concrete_base.jpg')",
              backgroundSize: "cover",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",

              border: "2px solid #3a3a3a",

              // объём + затемнение по краям (эффект старого бетона)
              boxShadow: `
                0 8px 20px rgba(0,0,0,0.75),
                inset 0 0 40px rgba(0,0,0,0.35),
                inset 0 -8px 15px rgba(0,0,0,0.25)
              `,

              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              overflow: "visible",

              opacity: 0,

              // падение + случайный наклон
              transform: `translate(${offsetX}px, ${offsetY - 40}px) rotate(${rot}deg)`,

              animation: `drop 0.65s cubic-bezier(.25,.75,.45,1.4) forwards`,
              animationDelay: `${index * 0.13}s`,
            }}
            onMouseDown={(e) =>
              (e.currentTarget.style.transform = "scale(0.97)")
            }
            onMouseUp={(e) =>
              (e.currentTarget.style.transform = "scale(1)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.transform = "scale(1)")
            }
          >
            <div
              style={{
                fontSize: "20px",
                fontWeight: "700",
                color: "#ffffff",
                textShadow: "0 3px 6px rgba(0,0,0,0.8)",
              }}
            >
              {section.title}
            </div>

            <div
              style={{
                opacity: 0.85,
                fontSize: "13px",
                color: "#e5e5e5",
                textShadow: "0 2px 3px rgba(0,0,0,0.6)",
                marginTop: "6px",
              }}
            >
              {section.description}
            </div>
          </div>
        );
      })}

      {/* ADMIN PANEL */}
      {isAdmin && (
        <div
          onClick={() => handleClick("admin")}
          style={{
            padding: "20px",
            borderRadius: "12px",
            backgroundImage: "url('/thule_hub_bot/images/concrete_base.jpg')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            border: "2px solid #3a3a3a",
            boxShadow: `
              0 8px 20px rgba(0,0,0,0.75),
              inset 0 0 40px rgba(0,0,0,0.35)
            `,
            cursor: "pointer",
            textAlign: "center",
            opacity: 0,
            transform: `translateY(-40px)`,
            animation: `drop 0.65s cubic-bezier(.25,.75,.45,1.4) forwards`,
            animationDelay: `${SECTIONS.length * 0.13}s`,
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: "700",
              color: "#4CAF50",
              textShadow: "0 2px 5px rgba(0,0,0,0.7)",
            }}
          >
            ⚙️ Админ-панель
          </div>
          <div
            style={{
              opacity: 0.85,
              fontSize: "13px",
              color: "#ddd",
              marginTop: "6px",
              textShadow: "0 1px 3px rgba(0,0,0,0.6)",
            }}
          >
            Управление контентом и товарами
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
