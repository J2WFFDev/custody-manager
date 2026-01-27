import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Kits from './pages/Kits';
import Audit from './pages/Audit';
import Users from './pages/Users';
import Approvals from './pages/Approvals';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/kits" element={<Kits />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/users" element={<Users />} />
          <Route path="/approvals" element={<Approvals />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
