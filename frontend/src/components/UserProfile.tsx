import React from 'react';

interface UserProfileProps {
  name: string;
  role: string;
  verifiedAdult: boolean;
}

const UserProfile: React.FC<UserProfileProps> = ({ name, role, verifiedAdult }) => {
  const getRoleBadgeColor = (role: string): string => {
    const colors: { [key: string]: string } = {
      admin: 'bg-purple-100 text-purple-800',
      armorer: 'bg-blue-100 text-blue-800',
      coach: 'bg-green-100 text-green-800',
      volunteer: 'bg-yellow-100 text-yellow-800',
      parent: 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="flex items-center gap-3">
      <div className="text-right">
        <div className="text-sm font-medium text-white">{name}</div>
        <div className="flex items-center gap-2 justify-end">
          <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${getRoleBadgeColor(role)}`}>
            {role}
          </span>
          {verifiedAdult && (
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-green-100 text-green-800" title="Verified Adult">
              ✓ Verified
            </span>
          )}
        </div>
      </div>
      <div className="w-10 h-10 rounded-full bg-white text-blue-600 flex items-center justify-center font-semibold">
        {name.charAt(0).toUpperCase()}
      </div>
    </div>
  );
};

export default UserProfile;
