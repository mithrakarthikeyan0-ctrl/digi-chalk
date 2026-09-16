export const PARENT_CHILDREN_DEMO = {
  aditi: {
    name: "Aditi",
    grade: "8B",
    subject: "Maths",
    unitTestScore: 82,
    scoreDelta: "Up 6 pts from last test",
    summaryEn: "Today Aditi covered fractions: writing them as decimals and simplifying to lowest terms. She completed the in-class quiz and marked two teacher bookmarks for revision.",
    summaryTa: "இன்று அதிதி பின்னங்கள் தலைப்பை கற்றார்: தசமங்களாக மாற்றுதல் மற்றும் எளிய வடிவில் எழுதுதல். வகுப்பறை வினாடி வினாவை முடித்து, ஆசிரியர் குறித்த இரண்டு முக்கிய பகுதிகளை தேர்வுக்காக குறித்து வைத்தார்.",
    scores: [
      { label: "Fractions quiz", value: 80, meta: "" },
      { label: "Science unit test", value: 56, meta: "" },
      { label: "English grammar", value: 88, meta: "" }
    ],
    recentAlert: "Aditi completed “Fractions” quiz — scored 4/5.",
    alertTime: "2:14 pm"
  },
  rohan: {
    name: "Rohan",
    grade: "5A",
    subject: "Science",
    unitTestScore: 74,
    scoreDelta: "Up 10 pts from last test",
    summaryEn: "Today Rohan learned about plant parts and photosynthesis in Science. He drew the leaf structure diagram and participated in the chalk quiz.",
    summaryTa: "இன்று ரோகன் அறிவியலில் தாவர பாகங்கள் மற்றும் ஒளிச்சேர்க்கை பற்றி கற்றார். இலை அமைப்பு வரைபடத்தை வரைந்து, வினாடி வினாவில் பங்கேற்றார்.",
    scores: [
      { label: "Plant biology quiz", value: 75, meta: "" },
      { label: "Maths multiplication", value: 70, meta: "" },
      { label: "Social studies map", value: 65, meta: "" }
    ],
    recentAlert: "Rohan completed “Plant biology” quiz — scored 3/5.",
    alertTime: "11:30 am"
  }
};

export const INITIAL_NOTIFICATIONS = [
  { id: 1, text: "New assignment: Fractions worksheet", read: false },
  { id: 2, text: "Class 8B Maths starts in 10 mins", read: false }
];

export const MOCK_LESSONS = [
  { id: "math_frac", title: "Fractions & Decimals", subject: "Maths", duration: 48 * 60, bookmarks: 2, date: "Today 10:15 AM", status: "recent" },
  { id: "geom_ang", title: "Angles & Triangles", subject: "Geometry", duration: 42 * 60, bookmarks: 1, date: "Yesterday", status: "recent" },
];
