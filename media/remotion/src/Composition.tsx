import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

const ink = "#142d3c";
const muted = "#526b78";
const teal = "#087e83";
const gold = "#d88b36";
const paper = "#f5f2e9";

const rise = (frame: number, start = 0) =>
  interpolate(frame, [start, start + 20], [28, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

const fade = (frame: number, start = 0) =>
  interpolate(frame, [start, start + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const Frame: React.FC<{ children: React.ReactNode; dark?: boolean }> = ({
  children,
  dark = false,
}) => (
  <AbsoluteFill
    style={{
      backgroundColor: dark ? ink : paper,
      color: dark ? paper : ink,
      fontFamily: "Arial, Helvetica, sans-serif",
      padding: "76px 92px",
      justifyContent: "center",
      overflow: "hidden",
    }}
  >
    {children}
  </AbsoluteFill>
);

const Eyebrow: React.FC<{ children: React.ReactNode; dark?: boolean }> = ({
  children,
  dark = false,
}) => (
  <div
    style={{
      color: dark ? "#8bd0cb" : teal,
      fontSize: 22,
      fontWeight: 700,
      letterSpacing: 3,
      textTransform: "uppercase",
      marginBottom: 24,
    }}
  >
    {children}
  </div>
);

const Title: React.FC<{ children: React.ReactNode; dark?: boolean }> = ({
  children,
  dark = false,
}) => (
  <div
    style={{
      color: dark ? paper : ink,
      fontSize: 58,
      lineHeight: 1.08,
      fontWeight: 700,
      letterSpacing: -1.6,
      maxWidth: 1040,
    }}
  >
    {children}
  </div>
);

const Copy: React.FC<{ children: React.ReactNode; dark?: boolean }> = ({
  children,
  dark = false,
}) => (
  <div
    style={{
      color: dark ? "#c2d1d5" : muted,
      fontSize: 28,
      lineHeight: 1.4,
      maxWidth: 850,
      marginTop: 24,
    }}
  >
    {children}
  </div>
);

const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Frame dark>
      <Img
        src={staticFile("gait_research_illustration.png")}
        style={{
          position: "absolute",
          right: -24,
          bottom: 0,
          width: 760,
          height: 430,
          objectFit: "cover",
          objectPosition: "center",
          opacity: 0.38,
          maskImage: "linear-gradient(90deg, transparent, black 48%)",
        }}
      />
      <div style={{ opacity: fade(frame), translate: `0 ${rise(frame)}px` }}>
        <Eyebrow dark>Parkinsonian gait biomarkers</Eyebrow>
        <Title dark>When does a walking measure tell us something real?</Title>
        <Copy dark>
          A clear look at severity, stability, measurement agreement, plus the
          limits of the evidence.
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          left: 92,
          bottom: 54,
          color: "#9eb4bb",
          fontSize: 18,
        }}
      >
        Research illustration. No participant data shown.
      </div>
    </Frame>
  );
};

const Association: React.FC = () => {
  const frame = useCurrentFrame();
  const left = 0.089;
  const right = 0.513;
  const point = 0.301;
  const scale = (value: number) => 260 + ((value + 0.1) / 0.8) * 760;
  return (
    <Frame>
      <div style={{ opacity: fade(frame), translate: `0 ${rise(frame)}px` }}>
        <Eyebrow>Finding one</Eyebrow>
        <Title>A severity link is present</Title>
        <Copy>
          A control trained walking score stayed associated with gait severity
          after accounting for pace.
        </Copy>
      </div>
      <div style={{ position: "relative", height: 180, marginTop: 46 }}>
        <div
          style={{
            position: "absolute",
            left: 260,
            right: 180,
            top: 75,
            height: 4,
            backgroundColor: "#c9d3d1",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: scale(left),
            width: scale(right) - scale(left),
            top: 63,
            height: 28,
            borderRadius: 20,
            backgroundColor: "#9bcac4",
            opacity: fade(frame, 14),
          }}
        />
        <div
          style={{
            position: "absolute",
            left: scale(point) - 11,
            top: 50,
            width: 28,
            height: 54,
            borderRadius: 16,
            backgroundColor: teal,
            scale: fade(frame, 20),
          }}
        />
        <div style={{ position: "absolute", left: 260, top: 122, fontSize: 20, color: muted }}>
          −0.1
        </div>
        <div style={{ position: "absolute", left: 990, top: 122, fontSize: 20, color: muted }}>
          0.7
        </div>
        <div
          style={{
            position: "absolute",
            left: scale(point) - 120,
            top: 0,
            width: 240,
            textAlign: "center",
            color: teal,
            fontSize: 25,
            fontWeight: 700,
          }}
        >
          0.301 effect
        </div>
      </div>
      <div style={{ color: muted, fontSize: 22 }}>
        95 percent confidence interval 0.089 to 0.513
      </div>
      <div style={{ color: muted, fontSize: 18, marginTop: 18 }}>
        Standardized association. Not a diagnosis or treatment effect.
      </div>
    </Frame>
  );
};

const Ranking: React.FC = () => {
  const frame = useCurrentFrame();
  const bars = [
    { label: "Row level splits", value: 99 },
    { label: "Participant level splits", value: 98 },
  ];
  return (
    <Frame dark>
      <div style={{ opacity: fade(frame), translate: `0 ${rise(frame)}px` }}>
        <Eyebrow dark>Finding two</Eyebrow>
        <Title dark>The score usually ranked severity better</Title>
        <Copy dark>
          Across 100 repeated grouped validations, the ranking gain appeared in
          almost every split.
        </Copy>
      </div>
      <div style={{ marginTop: 48 }}>
        {bars.map((bar, index) => {
          const width = interpolate(frame, [10 + index * 8, 48 + index * 8], [0, bar.value], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          return (
            <div key={bar.label} style={{ marginBottom: 30 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 22, marginBottom: 10 }}>
                <span>{bar.label}</span>
                <strong style={{ color: "#8bd0cb", fontSize: 28 }}>{bar.value}%</strong>
              </div>
              <div style={{ height: 18, borderRadius: 10, backgroundColor: "#38505a", overflow: "hidden" }}>
                <div style={{ width: `${width}%`, height: "100%", backgroundColor: "#68bdb4", borderRadius: 10 }} />
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 10, color: "#c2d1d5", fontSize: 24, lineHeight: 1.4 }}>
        Better ranking does not mean better exact score prediction. The result
        supports ranking only.
      </div>
    </Frame>
  );
};

const Boundaries: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = [
    { label: "Self paced stability", value: "0.647", color: gold },
    { label: "Hurried stability", value: "0.282", color: gold },
  ];
  return (
    <Frame>
      <div style={{ opacity: fade(frame), translate: `0 ${rise(frame)}px` }}>
        <Eyebrow>What remains unresolved</Eyebrow>
        <Title>Association is only one step</Title>
        <Copy>
          Eight reconstructed measurements agreed with the reference on 252
          trials. Long interval stability still missed its prespecified standard.
        </Copy>
      </div>
      <div style={{ display: "flex", gap: 24, marginTop: 48 }}>
        {rows.map((row, index) => (
          <div
            key={row.label}
            style={{
              flex: 1,
              minHeight: 152,
              border: "1px solid #d9ded8",
              borderRadius: 18,
              padding: 24,
              opacity: fade(frame, 14 + index * 8),
              translate: `0 ${rise(frame, 14 + index * 8)}px`,
            }}
          >
            <div style={{ color: muted, fontSize: 20 }}>{row.label}</div>
            <div style={{ color: row.color, fontSize: 48, fontWeight: 700, marginTop: 14 }}>
              ICC {row.value}
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 30, color: muted, fontSize: 23, lineHeight: 1.4 }}>
        Visits were at least six months apart. Short term repeatability,
        treatment response, plus broad external transport remain unproven.
      </div>
      <div style={{ position: "absolute", bottom: 38, right: 92, color: muted, fontSize: 17 }}>
        Secondary analysis. Not clinical guidance.
      </div>
    </Frame>
  );
};

export const MyComposition = () => (
  <>
    <Sequence durationInFrames={180}>
      <Intro />
    </Sequence>
    <Sequence from={180} durationInFrames={240}>
      <Association />
    </Sequence>
    <Sequence from={420} durationInFrames={240}>
      <Ranking />
    </Sequence>
    <Sequence from={660} durationInFrames={240}>
      <Boundaries />
    </Sequence>
  </>
);
