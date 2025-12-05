import React from 'react';

export default function AccountCreationForm() {
    const [formData, setFormData] = React.useState({
        name: "",
        courses: "",
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
        // TODO: call your backend API to insert into the MySQL User table
        console.log("Submitting:", formData);
        alert("Account created for: " + formData.name + " (" + (formData.isProfessor ? "Professor" : "Student") + ")");
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
                                Username:
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

                            <label>
                                Courses:
                                <input
                                    type="text"
                                    name="courses"
                                    value={formData.courses}
                                    onChange={handleChange}
                                    maxLength="50"
                                    className="note-title"
                                />
                            </label>

                        <div className="role-select" style={{ marginTop: "12px" }}>
                            <p>Select your role:</p>
                                <button type="button" onClick={() => setFormData(prev => ({ ...prev, isProfessor: false }))}>
                                    Student
                                </button>
                                <button type="button" onClick={() => setFormData(prev => ({ ...prev, isProfessor: true }))}>
                                    Professor
                                </button>
                            <p>Current selection: {formData.isProfessor ? "Professor" : "Student"}</p>
                        </div>

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

