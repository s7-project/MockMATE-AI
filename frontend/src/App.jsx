
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import ProtectedRoute from "./components/ProtectedRoute";


function App() {

  return (

    <BrowserRouter>

      <AuthProvider>

        <Routes>

          {/* Default route */}
          <Route
            path="/"
            element={<Navigate to="/login" replace />}
          />


          {/* Public routes */}
          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />


          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

          </Route>


          {/* Unknown routes */}
          <Route
            path="*"
            element={<Navigate to="/login" replace />}
          />

        </Routes>

      </AuthProvider>

    </BrowserRouter>

  );

}

export default App;
