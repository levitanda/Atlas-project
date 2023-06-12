import { Tabs, Tab } from 'react-bootstrap';
function TabbedLayout() {
    return (
        <Tabs defaultActiveKey="home" id="tabbed-layout">
            <Tab eventKey="home" title="Home">
                <h3>Home Content</h3>
                <p>This is the home tab content.</p>
            </Tab>
            <Tab eventKey="profile" title="Profile">
                <h3>Profile Content</h3>
                <p>This is the profile tab content.</p>
            </Tab>
            <Tab eventKey="contact" title="Contact">
                <h3>Contact Content</h3>
                <p>This is the contact tab content.</p>
            </Tab>
        </Tabs>
    );
}

export default TabbedLayout;
