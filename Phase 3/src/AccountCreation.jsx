import React from "react";

export default function AccountCreation() {
    const [formData, setFormData] = React.useState({
        name: "",
        password: "",
        isProfessor: false,
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // ---- NAVIGATION LOGIC ----
        if (formData.isProfessor) {
            window.location.href = "/professor.html";
        } else {
            window.location.href = "/student.html";
        }
    };

    return (
        <div>
            <div className="topbar">
                <span className="brand">Lobster Notes</span>
            </div>

            <div className="main" style={{ justifyContent: "center" }}>
                <div className="left" style={{ maxWidth: "480px" }}>
                    <div className="note-editor">
                        <h1 style={{ marginTop: 0 }}>Create Your Account</h1>

                        <form onSubmit={handleSubmit} className="account-form">
                            <label>
                                Name:
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                    maxLength="20"
                                    className="note-title"
                                />
                            </label>

                            <label>
                                Password:
                                <input
                                    type="text"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    maxLength="50"
                                    className="note-title"
                                />
                            </label>
                            
                            <div className="role-select" style={{ marginTop: "12px" }}>
                                <p>Select your role:</p>

                                <input
                                    type="radio"
                                    name="role"
                                    id="role1"
                                    value="Student"
                                    onClick={() =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            isProfessor: false,
                                        }))
                                    }
                                />
                                <label htmlFor="role1">Student</label>

                                <input
                                    type="radio"
                                    name="role"
                                    id="role2"
                                    value="Professor"
                                    onClick={() =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            isProfessor: true,
                                        }))
                                    }
                                />
                                <label htmlFor="role2">Professor</label>
                            </div>

                            <div style={{ height: "20px" }} />

                            <button type="submit" className="btn btn-primary">
                                Create Account
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
