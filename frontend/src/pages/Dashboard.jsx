
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Dashboard() {

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="dashboard-container">

      <h1>AI Mock Interview Dashboard</h1>

      <h2>
        Welcome, {user?.full_name || "Candidate"}!
      </h2>

      <p>
        Email: {user?.email}
      </p>

      <p>
        Your account is successfully authenticated.
      </p>

      <button onClick={handleLogout}>
        Logout
      </button>

    </div>
  );
}

export default Dashboard;
