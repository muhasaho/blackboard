from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from getpass import getpass

BASE_URL = "https://bb.ndsu.nodak.edu"

print("\n******Blackboard Downloader******\n\nSend Issues to muhasaho@gmail.com\n\n")

username = input("Enter Blackboard Username: ")
password = getpass("Enter Password (nothing will be displayed): ")


browser = webdriver.Chrome("./chromedriver")
browser.implicitly_wait(5)

browser.maximize_window()

# disable chrome pdf viewer
browser.get("chrome://settings-frame/content")
pdf_section = browser.find_element_by_id("pdf-section")
pdf_disable_checkbox = pdf_section.find_element_by_tag_name("input")
if not pdf_section.is_selected():
    pdf_disable_checkbox.click()


def main():
    browser.get(BASE_URL)
    username_input = browser.find_element_by_id("user_id")
    username_input.send_keys(username)
    password_input = browser.find_element_by_id("password")
    password_input.send_keys(password)
    login_button = browser.find_element_by_id("entry-login")
    login_button.click()

    # go to courses
    browser.get(BASE_URL + "/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_2_1")

    # find course links
    course_links_elements = browser.find_elements_by_partial_link_text("-NDSU-")
    course_names_and_links = [(el.get_attribute("text"), el.get_attribute("href")) for el in course_links_elements]

    # loop through the courses
    for course_name, course_link in course_names_and_links:
        input("{}\n****Press Enter to download".format(course_name))
        browser.get(course_link)
        course_content_link_elements = browser.find_elements_by_partial_link_text("Course ")
        course_content_links = [x.get_attribute("href") for x in course_content_link_elements]

        # loop through the different Content Areas. eg `Course Content`, `Course Information`
        for content_link in course_content_links:
            browser.get(content_link)
            content_box = browser.find_element_by_id("content")
            file_or_folder_elements = content_box.find_elements_by_xpath(".//a[@href]")  # find all links
            file_or_folder_texts_and_links = [(x.get_attribute("text"), x.get_attribute("href")) for x in file_or_folder_elements]
            recursive_download(file_or_folder_texts_and_links)
    browser.quit()


def recursive_download(starting_file_or_folder_texts_and_links):
    starting_location = browser.current_url
    for file_or_folder_name, file_or_folder_link in starting_file_or_folder_texts_and_links:
        print("...Downloading {}".format(file_or_folder_name))
        browser.get(file_or_folder_link)
        current_location = browser.current_url
        if starting_location != current_location:
            try:
                content_box = browser.find_element_by_id("content")
                file_or_folder_elements = content_box.find_elements_by_xpath(".//a[@href]")  # find all links
                new_file_or_folder_texts_and_links = [(x.get_attribute("text"), x.get_attribute("href")) for x in
                                                      file_or_folder_elements]
                recursive_download(new_file_or_folder_texts_and_links)
            except NoSuchElementException:
                print("Warning: Cant download {}".format(file_or_folder_name))
                browser.back()

if __name__ == "__main__":
    main()
