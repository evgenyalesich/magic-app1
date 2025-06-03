export const setUserData = (data) => {
  localStorage.setItem("user", JSON.stringify(data));
};

export const getUserData = () => {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
};

export const isAdmin = () => {
  const user = getUserData();
  return user ? user.is_admin : false;
};
