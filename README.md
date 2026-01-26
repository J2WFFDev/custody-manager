# WilcoSS Custody & Equipment Manager

A web-based custody tracking system for youth shooting sports organizations to manage firearm kits, equipment, and maintenance with full audit trails.

## 🎯 Purpose

This system provides:
- **QR-based check-in/check-out** for equipment and firearm kits
- **Role-based access control** (Admin, Armorer, Coach, Volunteer, Parent)
- **Custody event tracking** with append-only audit logs
- **Maintenance scheduling** and history
- **Multi-role approval workflows** for off-site custody
- **Responsibility attestation** for legal compliance

## 🏗️ Tech Stack

### Frontend
- **React** with **Vite** - Fast, modern development
- **TailwindCSS** - Utility-first styling
- **html5-qrcode** - QR code scanning
- **Deployed on Vercel**

### Backend
- **FastAPI** (Python) - High-performance async API
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **OAuth 2.0** - Google & Microsoft authentication
- **JWT** - Session management
- **Deployed on Railway**

## 📋 Features

### Authentication & Identity
- Google and Microsoft OAuth login
- Role-based permissions (Admin, Armorer, Coach, Volunteer, Parent)
- "Verified Adult" flag for off-site custody authorization

### QR Operations
- Generate QR codes for kits
- Mobile-first scanning interface
- Manual code entry fallback

### Custody Management
- On-premises check-out/check-in
- Off-site custody with multi-role approval
- Custody transfer between users
- Responsibility attestation
- Lost/found reporting
- Soft warnings (non-blocking alerts)

### Maintenance Tracking
- Open/close maintenance events
- Round count and parts tracking
- Maintenance history timeline
- Overdue maintenance warnings

### Audit & Compliance
- Append-only event logs (no deletions)
- Complete custody timeline per kit/user
- CSV/JSON export for audits
- Encrypted serial numbers at rest

## 📖 Documentation

- **[User Stories](USER_STORIES.md)** - Feature requirements by user role
- **[Architecture Guide](ARCHITECTURE.md)** - Technical design and decisions
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to this project
- **[Deployment Guide](DEPLOYMENT.md)** - Vercel and Railway deployment instructions

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **PostgreSQL** 14+
- **Git**

### Local Development Setup

#### 1. Clone the repository
```bash
git clone https://github.com/J2WFFDev/custody-manager.git
cd custody-manager
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

#### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

#### 4. Database Setup
```bash
# Create PostgreSQL database
createdb custody_manager

# Run migrations
cd backend
alembic upgrade head
```

### Environment Variables

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

#### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/custody_manager
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
JWT_SECRET_KEY=your_secret_key
```

## 🗂️ Project Structure

```
custody-manager/
├── frontend/           # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── USER_STORIES.md     # User stories and requirements
├── ARCHITECTURE.md     # Technical architecture
└── README.md           # This file
```

## 🚀 Deployment

The application is deployed using:
- **Frontend**: [Vercel](https://vercel.com) - Automatic deployments from `main` branch
- **Backend**: [Railway](https://railway.app) - Automatic deployments with PostgreSQL

**Production URLs:**
- Frontend: `https://[your-project].vercel.app`
- Backend API: `https://[your-backend].railway.app`

**Preview Deployments:**
- Every pull request automatically gets a preview deployment on Vercel
- Preview URL is posted as a comment on the PR

For detailed deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## 📊 Issue Tracking

All development tasks are tracked as GitHub Issues organized by epic:
- [Epic #1: Project Setup](https://github.com/J2WFFDev/custody-manager/issues/1)
- [Epic #2: Authentication](https://github.com/J2WFFDev/custody-manager/issues/2)
- [Epic #3: QR Operations](https://github.com/J2WFFDev/custody-manager/issues/3)
- [Epic #4: Custody Management](https://github.com/J2WFFDev/custody-manager/issues/4)
- [Epic #5: Maintenance Tracking](https://github.com/J2WFFDev/custody-manager/issues/5)
- [Epic #6: Audit Trail](https://github.com/J2WFFDev/custody-manager/issues/6)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to submit pull requests.

## 📄 License

This project is private and proprietary.

## 📧 Contact

**Project Owner:** J2WFFDev  
**Repository:** https://github.com/J2WFFDev/custody-manager

---

Built with ❤️ for youth shooting sports safety and accountability.