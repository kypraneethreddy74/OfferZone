import React from "react";
import { PowerBIEmbed } from "powerbi-client-react";
import { models } from "powerbi-client";

const PowerBIDashboardPage = () => {
  return (
    <div style={{ padding: "20px", background: "#f4f6f9", minHeight: "100vh" }}>
      <h2 style={{ marginBottom: "15px", fontSize: "22px", fontWeight: "600" }}>
        📊 Power BI Dashboard
      </h2>

      <div
        style={{
          height: "85vh",
          background: "#fff",
          borderRadius: "12px",
          boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
          overflow: "hidden",
        }}
      >
        <PowerBIEmbed
          embedConfig={{
            type: "report",
            id: "YOUR_REPORT_ID",
            embedUrl: "YOUR_EMBED_URL",
            accessToken: "YOUR_ACCESS_TOKEN",
            tokenType: models.TokenType.Embed,
            settings: {
              panes: {
                filters: { visible: true },
                pageNavigation: { visible: true },
              },
              background: models.BackgroundType.Transparent,
            },
          }}
          cssClassName="powerbi-frame"
        />
      </div>
    </div>
  );
};

export default PowerBIDashboardPage;
