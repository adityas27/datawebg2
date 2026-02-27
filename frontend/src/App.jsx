import { Routes, Route, BrowserRouter as Router } from "react-router-dom";
// import LandingPage from "./pages/LandingPage";
import Register from "./pages/Register";
import LogIn from "./pages/Login";
const AppContent = () => {
  return (
    <Routes>
      {/* <Route path="/" element={<LandingPage />} /> */}
      <Route path="/register" element={<Register />} />
      {/* <Route path="/about" element={<AboutUs />} /> */}
      <Route path="/login" element={<LogIn />} />
    </Routes>
  );
}

function App() {
  return(
    <Router>
      <AppContent/>
    </Router>
  )
}

export default App;