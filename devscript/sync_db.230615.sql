drop table django_migrations;

drop table auth_group_permissions;

drop table cofk_user_groups;

drop table auth_group;

drop table cofk_user_user_permissions;

drop table auth_permission;

drop table django_admin_log;

drop table django_content_type;

alter table cofk_lookup_catalogue
    alter column catalogue_id set default nextval('cofk_lookup_catalogue_id_seq'::regclass);

drop index cofk_lookup_catalogue_catalogue_code_ca21e20f_like;

drop index cofk_lookup_catalogue_catalogue_name_656ef550_like;

alter table cofk_lookup_catalogue
drop constraint cofk_lookup_catalogue_catalogue_code_key;

alter table cofk_lookup_catalogue
drop constraint cofk_lookup_catalogue_catalogue_name_key;

alter table cofk_lookup_document_type
    alter column document_type_id set default nextval('cofk_lookup_document_type_id_seq'::regclass);

drop index cofk_lookup_document_type_document_type_code_cabc511c_like;

alter table cofk_lookup_document_type
drop constraint cofk_lookup_document_type_document_type_code_key;

alter table cofk_union_comment
    alter column comment_id set default nextval('cofk_union_comment_id_seq'::regclass);

alter table cofk_union_comment
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_comment
    alter column creation_user set default "current_user"();

alter table cofk_union_comment
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_comment
    alter column change_user set default "current_user"();

-- Alter Turn not supported

alter table cofk_union_image
    alter column image_id set default nextval('cofk_union_image_id_seq'::regclass);

alter table cofk_union_image
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_image
    alter column creation_user set default "current_user"();

alter table cofk_union_image
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_image
    alter column change_user set default "current_user"();

-- Alter Turn not supported

alter table cofk_union_nationality
    alter column nationality_id set default nextval('cofk_union_nationality_id_seq'::regclass);

alter table cofk_union_org_type
    alter column org_type_id set default nextval('cofk_union_org_type_id_seq'::regclass);

alter table cofk_union_relationship_type
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_relationship_type
    alter column creation_user set default "current_user"();

alter table cofk_union_relationship_type
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_relationship_type
    alter column change_user set default "current_user"();

drop index cofk_union_relationship_type_relationship_code_146f9956_like;

-- Alter Turn not supported

alter table cofk_union_resource
    alter column resource_id set default nextval('cofk_union_resource_id_seq'::regclass);

alter table cofk_union_resource
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_resource
    alter column creation_user set default "current_user"();

alter table cofk_union_resource
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_resource
    alter column change_user set default "current_user"();

-- Alter Turn not supported

alter table cofk_union_role_category
    alter column role_category_id set default nextval('cofk_union_role_category_id_seq'::regclass);

alter table cofk_union_speed_entry_text
    alter column speed_entry_text_id set default nextval('cofk_union_speed_entry_text_id_seq'::regclass);

alter table cofk_union_subject
    alter column subject_id set default nextval('cofk_union_subject_id_seq'::regclass);

alter table cofk_user_saved_queries
    alter column query_id set default nextval('cofk_user_saved_queries_id_seq'::regclass);

alter table cofk_user_saved_queries
    alter column query_title set default ''::text;

alter table cofk_user_saved_queries
    alter column query_order_by set default ''::character varying;

alter table cofk_user_saved_queries
    alter column query_sort_descending set default 0;

alter table cofk_user_saved_queries
    alter column query_entries_per_page set default 20;

alter table cofk_user_saved_queries
    alter column query_record_layout set default 'across_page'::character varying;

alter table cofk_user_saved_queries
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_user_saved_queries
    alter column creation_timestamp set default now();

alter table cofk_user_saved_queries
    alter column username set default "current_user"();

-- column reordering is not supported cofk_user_saved_queries.username

drop index cofk_user_saved_query_username_169b9148;

drop index cofk_user_saved_query_username_169b9148_like;

alter table cofk_user_saved_queries
drop constraint cofk_user_saved_query_username_169b9148_fk_cofk_user_username;

drop table cofk_user;

alter table iso_639_language_codes
    alter column language_id set default nextval('iso_639_language_codes_id_seq'::regclass);

drop index iso_639_language_codes_code_639_3_b3193465_like;

alter table iso_639_language_codes
drop constraint iso_639_language_codes_language_id_key;

drop index cofk_union_favourite_language_language_code_a1ad744a_like;

alter table cofk_union_favourite_language
drop constraint cofk_union_favourite_language_code_a1ad744a_fk_iso_639_l;

alter table cofk_user_saved_query_selection
    alter column selection_id set default nextval('cofk_user_saved_query_selection_id_seq'::regclass);

-- column reordering is not supported cofk_user_saved_query_selection.query_id

drop index cofk_user_saved_query_selection_query_id_5a4ad6e0;

alter table cofk_user_saved_query_selection
drop constraint cofk_user_saved_quer_query_id_5a4ad6e0_fk_cofk_user;

alter table cofk_user_saved_queries
drop constraint cofk_user_saved_query_pkey;

alter table cofk_union_publication
    alter column publication_id set default nextval('cofk_union_publication_id_seq'::regclass);

alter table cofk_union_publication
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_publication
    alter column change_user set default "current_user"();

-- Alter Turn not supported

drop table cofk_location_comment_map;

drop table cofk_location_image_map;

drop table cofk_location_resource_map;

create table cofk_union_queryable_work
(
    iwork_id                   integer                                    not null
        primary key,
    work_id                    varchar(100)                               not null
        constraint cofk_uniq_union_queryable_work_id
            unique
        constraint cofk_union_queryable_work_fk_work_id
            references cofk_union_work
            on delete cascade,
    description                text,
    date_of_work_std           date,
    date_of_work_std_year      integer,
    date_of_work_std_month     integer,
    date_of_work_std_day       integer,
    date_of_work_as_marked     varchar(250),
    date_of_work_inferred      smallint     default 0                     not null,
    date_of_work_uncertain     smallint     default 0                     not null,
    date_of_work_approx        smallint     default 0                     not null,
    creators_searchable        text         default ''::text              not null,
    creators_for_display       text         default ''::text              not null,
    authors_as_marked          text,
    notes_on_authors           text,
    authors_inferred           smallint     default 0                     not null,
    authors_uncertain          smallint     default 0                     not null,
    addressees_searchable      text         default ''::text              not null,
    addressees_for_display     text         default ''::text              not null,
    addressees_as_marked       text,
    addressees_inferred        smallint     default 0                     not null,
    addressees_uncertain       smallint     default 0                     not null,
    places_from_searchable     text         default ''::text              not null,
    places_from_for_display    text         default ''::text              not null,
    origin_as_marked           text,
    origin_inferred            smallint     default 0                     not null,
    origin_uncertain           smallint     default 0                     not null,
    places_to_searchable       text         default ''::text              not null,
    places_to_for_display      text         default ''::text              not null,
    destination_as_marked      text,
    destination_inferred       smallint     default 0                     not null,
    destination_uncertain      smallint     default 0                     not null,
    manifestations_searchable  text         default ''::text              not null,
    manifestations_for_display text         default ''::text              not null,
    abstract                   text,
    keywords                   text,
    people_mentioned           text,
    images                     text,
    related_resources          text,
    language_of_work           varchar(255),
    work_is_translation        smallint     default 0                     not null,
    flags                      text,
    edit_status                varchar(3)   default ''::character varying not null,
    general_notes              text,
    original_catalogue         varchar(100) default ''::character varying not null,
    accession_code             varchar(1000),
    work_to_be_deleted         smallint     default 0                     not null,
    change_timestamp           timestamp    default now(),
    change_user                varchar(50)  default "current_user"()      not null,
    drawer                     varchar(50),
    editors_notes              text,
    manifestation_type         varchar(50),
    original_notes             text,
    relevant_to_cofk           varchar(1)   default ''::character varying not null,
    subjects                   text
);

alter table cofk_union_queryable_work
    owner to postgres;

create trigger cofk_union_queryable_work_trg_set_change_cols
    before update
    on cofk_union_queryable_work
    for each row
    execute procedure dbf_cofk_set_change_cols();

alter table cofk_union_location
    alter column location_id set default nextval('cofk_union_location_id_seq'::regclass);

alter table cofk_union_location
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_location
    alter column creation_user set default "current_user"();

alter table cofk_union_location
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_location
    alter column change_user set default "current_user"();

-- Alter Turn not supported

alter table cofk_collect_addressee_of_work
    add constraint cofk_collect_addressee_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_author_of_work
    add constraint cofk_collect_author_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_person_comment_map;

alter table cofk_collect_destination_of_work
    add constraint cofk_collect_destination_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_person_image_map;

alter table cofk_collect_image_of_manif
    add constraint cofk_collect_image_of_manif_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_institution
    add constraint cofk_collect_institution_fk_union_id
        foreign key (union_institution_id) references cofk_union_institution
            on delete set null;

alter table cofk_collect_institution
    add constraint cofk_collect_institution_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_person_location_map;

drop table cofk_person_resource_map;

alter table cofk_collect_institution_resource
    add constraint cofk_collect_institution_resource_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_union_person
    alter column iperson_id set default nextval('cofk_union_person_iperson_id_seq'::regclass);

alter table cofk_union_person
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_person
    alter column creation_user set default "current_user"();

alter table cofk_union_person
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_person
    alter column change_user set default "current_user"();

-- column reordering is not supported cofk_union_person.organisation_type

drop index cofk_union_person_person_id_49f4748f_like;

drop index cofk_union_person_organisation_type_37bee9de;

alter table cofk_union_person
drop constraint cofk_union_person_organisation_type_37bee9de_fk_cofk_unio;

-- Alter Turn not supported

alter table cofk_collect_language_of_work
    add constraint cofk_collect_language_of_work_fk_language_id
        foreign key (language_code) references iso_639_language_codes;

alter table cofk_collect_language_of_work
    add constraint cofk_collect_language_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_location
    add constraint cofk_collect_location_fk_union_id
        foreign key (union_location_id) references cofk_union_location
            on delete set null;

alter table cofk_collect_location
    add constraint cofk_collect_location_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_person_role_map;

alter table cofk_collect_location_resource
    add constraint cofk_collect_location_resource_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_manifestation
    add constraint cofk_collect_manifestation_fk_union_id
        foreign key (union_manifestation_id) references cofk_union_manifestation
            on delete set null;

alter table cofk_collect_manifestation
    add constraint cofk_collect_manifestation_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_occupation_of_person
    add constraint cofk_collect_occupation_of_person_fk_occupation_id
        foreign key (occupation_id) references cofk_union_role_category
            on delete cascade;

alter table cofk_collect_occupation_of_person
    add constraint cofk_collect_occupation_of_person_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_person_person_map;

alter table cofk_collect_origin_of_work
    add constraint cofk_collect_origin_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_person
    add constraint cofk_collect_person_fk_union_id
        foreign key (person_id) references cofk_union_person
            on delete set null;

alter table cofk_collect_person
    add constraint cofk_collect_person_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_person_mentioned_in_work
    add constraint cofk_collect_person_mentioned_in_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_person_resource
    add constraint cofk_collect_person_resource_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_place_mentioned_in_work
    add constraint cofk_collect_place_mentioned_in_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_subject_of_work
    add constraint cofk_collect_subject_of_work_fk_subject_id
        foreign key (subject_id) references cofk_union_subject
            on delete cascade;

alter table cofk_collect_subject_of_work
    add constraint cofk_collect_subject_of_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_collect_tool_session
    add constraint cofk_collect_tool_uniq_session_code
        unique (session_code);

alter table cofk_collect_tool_user
    add constraint cofk_collect_tool_user_uniq_email
        unique (tool_user_email);

alter table cofk_collect_tool_session
    add constraint cofk_collect_tool_fk_sessions_username
        foreign key (username) references cofk_collect_tool_user (tool_user_email)
            on update cascade on delete cascade;

alter table cofk_collect_upload
    add constraint cofk_collect_fk_upload_status
        foreign key (upload_status) references cofk_collect_status;

alter table cofk_collect_work
    add constraint cofk_collect_fk_work_status
        foreign key (upload_status) references cofk_collect_status;

alter table cofk_collect_work
    add constraint cofk_collect_work_fk_union_id
        foreign key (work_id) references cofk_union_work
            on delete set null;

alter table cofk_collect_work
    add constraint cofk_collect_work_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

alter table cofk_union_work
    alter column iwork_id set default nextval('cofk_union_work_iwork_id_seq'::regclass);

alter table cofk_union_work
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_work
    alter column creation_user set default "current_user"();

alter table cofk_union_work
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_work
    alter column change_user set default "current_user"();

-- column reordering is not supported cofk_union_work.original_catalogue

drop index cofk_union_work_work_id_b789e904_like;

drop index cofk_union_work_original_catalogue_a7fe2240;

drop index cofk_union_work_original_catalogue_a7fe2240_like;

-- Alter Turn not supported

drop table cofk_work_work_map;

alter table cofk_collect_work_resource
    add constraint cofk_collect_work_resource_fk_upload_id
        foreign key (upload_id) references cofk_collect_upload;

drop table cofk_work_subject_map;

alter table cofk_collect_work_summary
    add work_id_in_tool integer not null;

-- column reordering is not supported cofk_collect_work_summary.work_id_in_tool

drop table cofk_work_resource_map;

drop table cofk_work_person_map;

drop table cofk_work_location_map;

create table cofk_help_pages
(
    page_id        integer default nextval('cofk_help_pages_page_id_seq'::regclass) not null
        primary key,
    page_title     varchar(500)                                                     not null,
    custom_url     varchar(500),
    published_text text    default 'Sorry, no help currently available.'::text      not null,
    draft_text     text
);

alter table cofk_help_pages
    owner to postgres;

drop table cofk_work_comment_map;

alter table cofk_lookup_catalogue
    add constraint cofk_uniq_lookup_catalogue_code
        unique (catalogue_code);

alter table cofk_lookup_catalogue
    add constraint cofk_uniq_lookup_catalogue_name
        unique (catalogue_name);

alter table cofk_lookup_document_type
    add constraint cofk_lookup_uniq_document_type_code
        unique (document_type_code);

-- column reordering is not supported cofk_union_language_of_work.work_id

-- column reordering is not supported cofk_union_language_of_work.language_code

drop index cofk_union_language_of_work_language_code_80b7ec36;

drop index cofk_union_language_of_work_language_code_80b7ec36_like;

drop index cofk_union_language_of_work_work_id_cbe641cb;

drop index cofk_union_language_of_work_work_id_cbe641cb_like;

alter table cofk_union_language_of_work
drop constraint cofk_union_language_of_work_pkey;

alter table cofk_union_language_of_work
drop column lang_work_id;

alter table cofk_union_language_of_work
drop constraint cofk_union_language_of_work_work_id_language_code_137a8af7_uniq;

alter table cofk_union_language_of_work
drop constraint cofk_union_language__language_code_80b7ec36_fk_iso_639_l;

alter table cofk_union_language_of_work
drop constraint cofk_union_language__work_id_cbe641cb_fk_cofk_unio;

create table cofk_menu
(
    menu_item_id     integer     default nextval('cofk_menu_item_id_seq'::regclass) not null
        primary key,
    menu_item_name   text                                                           not null,
    menu_order       integer     default nextval('cofk_menu_order_seq'::regclass),
    parent_id        integer
        constraint cofk_fk_tracking_menu_parent_id
            references cofk_menu,
    has_children     integer     default 0                                          not null,
    class_name       varchar(100),
    method_name      varchar(100),
    user_restriction varchar(30) default ''::character varying                      not null,
    hidden_parent    integer,
    called_as_popup  integer     default 0                                          not null
        constraint cofk_chk_menu_item_called_as_popup
            check ((called_as_popup = 0) OR (called_as_popup = 1)),
    collection       varchar(20) default ''::character varying                      not null,
    constraint cofk_chk_item_is_submenu_or_form
        check (((has_children = 0) AND (class_name IS NOT NULL) AND (method_name IS NOT NULL)) OR
               ((has_children = 1) AND (class_name IS NULL) AND (method_name IS NULL)))
);

alter table cofk_menu
    owner to postgres;

create table cofk_help_options
(
    option_id       integer      default nextval('cofk_help_options_option_id_seq'::regclass) not null
        primary key,
    menu_item_id    integer
        constraint cofk_fk_help_option_menu_item
            references cofk_menu,
    button_name     varchar(100) default ''::character varying                                not null,
    help_page_id    integer                                                                   not null
        constraint cofk_fk_help_option_page
            references cofk_help_pages,
    order_in_manual integer      default 0                                                    not null,
    menu_depth      integer      default 0                                                    not null,
    constraint cofk_uniq_help_option_menu_item_button
        unique (menu_item_id, button_name)
);

alter table cofk_help_options
    owner to postgres;

create table cofk_report_groups
(
    report_group_id      integer default nextval('cofk_report_groups_report_group_id_seq'::regclass) not null
        primary key,
    report_group_title   text,
    report_group_order   integer default 1                                                           not null,
    on_main_reports_menu integer default 0                                                           not null,
    report_group_code    varchar(100)
);

alter table cofk_report_groups
    owner to postgres;

create table cofk_report_outputs
(
    output_id   varchar(250) default ''::character varying not null,
    line_number integer      default 0                     not null,
    line_text   text
);

alter table cofk_report_outputs
    owner to postgres;

create table cofk_reports
(
    report_id           integer  default nextval('cofk_reports_report_id_seq'::regclass) not null
        primary key,
    report_title        text,
    class_name          varchar(40),
    method_name         varchar(40),
    report_group_id     integer
        constraint cofkfk_reports_report_group_id
            references cofk_report_groups,
    menu_item_id        integer
        constraint cofkfk_reports_menu_item_id
            references cofk_menu,
    has_csv_option      integer  default 0                                               not null,
    is_dummy_option     integer  default 0                                               not null,
    report_code         varchar(100),
    parm_list           text,
    parm_titles         text,
    prompt_for_parms    smallint default 0                                               not null,
    default_parm_values text,
    parm_methods        text,
    report_help         text
);

alter table cofk_reports
    owner to postgres;

create table cofk_roles
(
    role_id   integer     default nextval('cofk_roles_role_id_seq'::regclass) not null
        primary key,
    role_code varchar(20) default ''::character varying                       not null
        constraint cofk_uniq_role_code
        unique,
    role_name text        default ''::text                                    not null
        constraint cofk_uniq_role_name
        unique
);

alter table cofk_roles
    owner to postgres;

alter table cofk_union_person
    add constraint cofk_uniq_union_iperson_id
        unique (iperson_id);

alter table cofk_collect_person
    add constraint cofk_collect_person_fk_union_iid
        foreign key (union_iperson_id) references cofk_union_person (iperson_id)
            on delete set null;

alter table cofk_union_person
    add constraint cofk_union_fk_org_type
        foreign key (organisation_type) references cofk_union_org_type;

create trigger cofk_union_person_trg_cascade03_del
    after delete
    on cofk_union_person
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_person_trg_cascade03_ins
    after insert
    on cofk_union_person
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_person_trg_cascade03_upd
    after update
    on cofk_union_person
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_person_trg_set_change_cols
    before update
    on cofk_union_person
    for each row
    execute procedure dbf_cofk_set_change_cols();

drop table cofk_institution_image_map;

drop table cofk_institution_resource_map;

alter table cofk_union_institution
    alter column institution_id set default nextval('cofk_union_institution_id_seq'::regclass);

alter table cofk_union_institution
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_institution
    alter column creation_user set default "current_user"();

alter table cofk_union_institution
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_institution
    alter column change_user set default "current_user"();

-- Alter Turn not supported

alter table cofk_union_work
    add language_of_work varchar(255);

-- column reordering is not supported cofk_union_work.language_of_work

alter table cofk_union_work
    add constraint cofk_uniq_union_iwork_id
        unique (iwork_id);

alter table cofk_collect_work
    add constraint cofk_collect_work_fk_union_iid
        foreign key (union_iwork_id) references cofk_union_work (iwork_id)
            on delete set null;

alter table cofk_union_work
    add constraint cofk_union_work_fk_original_catalogue
        foreign key (original_catalogue) references cofk_lookup_catalogue (catalogue_code)
            on update cascade;

create trigger cofk_union_work_trg_cascade01_del
    after delete
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade01_work_changes();

create trigger cofk_union_work_trg_cascade01_ins
    after insert
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade01_work_changes();

create trigger cofk_union_work_trg_cascade01_upd
    after update
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade01_work_changes();

create trigger cofk_union_work_trg_cascade03_del
    after delete
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_work_trg_cascade03_ins
    after insert
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_work_trg_cascade03_upd
    after update
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_work_trg_set_change_cols
    before update
    on cofk_union_work
    for each row
    execute procedure dbf_cofk_set_change_cols();

drop table cofk_manif_image_map;

alter table cofk_union_manifestation
alter column creation_timestamp type timestamp using creation_timestamp::timestamp;

alter table cofk_union_manifestation
    alter column creation_user set default "current_user"();

alter table cofk_union_manifestation
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_manifestation
    alter column change_user set default "current_user"();

drop index cofk_union_manifestation_manifestation_id_2627abe2_like;

drop index cofk_union_manifestation_work_id_0aa9a6be;

drop index cofk_union_manifestation_work_id_0aa9a6be_like;

alter table cofk_union_manifestation
drop constraint cofk_union_manifesta_work_id_0aa9a6be_fk_cofk_unio;

alter table cofk_union_manifestation
drop column work_id;

-- Alter Turn not supported

drop table cofk_manif_person_map;

drop table cofk_manif_manif_map;

drop table cofk_manif_inst_map;

create trigger cofk_union_comment_trg_cascade03_del
    after delete
    on cofk_union_comment
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_comment_trg_cascade03_ins
    after insert
    on cofk_union_comment
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_comment_trg_cascade03_upd
    after update
    on cofk_union_comment
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_comment_trg_set_change_cols
    before update
    on cofk_union_comment
    for each row
    execute procedure dbf_cofk_set_change_cols();

drop table cofk_manif_comment_map;

-- column reordering is not supported cofk_union_language_of_manifestation.manifestation_id

-- column reordering is not supported cofk_union_language_of_manifestation.language_code

drop index cofk_union_language_of_manifestation_language_code_b7cdf192;

drop index cofk_union_language_of_m_language_code_b7cdf192_like;

drop index cofk_union_language_of_manifestation_manifestation_id_72b027d0;

drop index cofk_union_language_of_m_manifestation_id_72b027d0_like;

alter table cofk_union_language_of_manifestation
drop constraint cofk_union_language_of_manifestation_pkey;

alter table cofk_union_language_of_manifestation
drop column lang_manif_id;

alter table cofk_union_language_of_manifestation
drop constraint cofk_union_language_of_m_manifestation_id_languag_3a20f2b9_uniq;

alter table cofk_union_language_of_manifestation
drop constraint cofk_union_language__language_code_b7cdf192_fk_iso_639_l;

alter table cofk_union_language_of_manifestation
drop constraint cofk_union_language__manifestation_id_72b027d0_fk_cofk_unio;

alter table cofk_union_favourite_language
    add constraint cofk_union_fk_language_code
        foreign key (language_code) references iso_639_language_codes
            on delete cascade;

create trigger cofk_union_image_trg_cascade03_upd
    after update
    on cofk_union_image
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_image_trg_set_change_cols
    before update
    on cofk_union_image
    for each row
    execute procedure dbf_cofk_set_change_cols();

create trigger cofk_union_institution_trg_set_change_cols
    before update
    on cofk_union_institution
    for each row
    execute procedure dbf_cofk_set_change_cols();

alter table cofk_union_language_of_manifestation
    add primary key (manifestation_id, language_code);

alter table cofk_union_language_of_manifestation
    add constraint cofk_union_fk_language_code
        foreign key (language_code) references iso_639_language_codes
            on delete cascade;

alter table cofk_union_language_of_manifestation
    add constraint cofk_union_fk_manifestation_id
        foreign key (manifestation_id) references cofk_union_manifestation
            on delete cascade;

create trigger cofk_union_language_of_manifestation_trg_cascade03_del
    after delete
    on cofk_union_language_of_manifestation
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_manifestation();

create trigger cofk_union_language_of_manifestation_trg_cascade03_ins
    after insert
    on cofk_union_language_of_manifestation
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_manifestation();

create trigger cofk_union_language_of_manifestation_trg_cascade03_upd
    after update
    on cofk_union_language_of_manifestation
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_manifestation();

alter table cofk_union_language_of_work
    add primary key (work_id, language_code);

alter table cofk_union_language_of_work
    add constraint cofk_union_fk_language_code
        foreign key (language_code) references iso_639_language_codes
            on delete cascade;

alter table cofk_union_language_of_work
    add constraint cofk_union_fk_work_id
        foreign key (work_id) references cofk_union_work
            on delete cascade;

create trigger cofk_union_language_of_work_trg_cascade03_del
    after delete
    on cofk_union_language_of_work
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_work();

create trigger cofk_union_language_of_work_trg_cascade03_ins
    after insert
    on cofk_union_language_of_work
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_work();

create trigger cofk_union_language_of_work_trg_cascade03_upd
    after update
    on cofk_union_language_of_work
    for each row
    execute procedure dbf_cofk_union_refresh_language_of_work();

create trigger cofk_union_location_trg_cascade03_del
    after delete
    on cofk_union_location
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_location_trg_cascade03_ins
    after insert
    on cofk_union_location
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_location_trg_cascade03_upd
    after update
    on cofk_union_location
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_location_trg_set_change_cols
    before update
    on cofk_union_location
    for each row
    execute procedure dbf_cofk_set_change_cols();

alter table cofk_union_audit_literal
    alter column audit_id set default nextval('cofk_union_audit_id_seq'::regclass);

alter table cofk_union_audit_literal
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_audit_literal
    alter column change_user set default "current_user"();

create table cofk_union_relationship
(
    relationship_id         integer     default nextval('cofk_union_relationship_id_seq'::regclass) not null
        primary key,
    left_table_name         varchar(100)                                                            not null,
    left_id_value           varchar(100)                                                            not null,
    relationship_type       varchar(100)                                                            not null
        constraint cofk_fk_union_relationship_type
            references cofk_union_relationship_type,
    right_table_name        varchar(100)                                                            not null,
    right_id_value          varchar(100)                                                            not null,
    relationship_valid_from timestamp,
    relationship_valid_till timestamp,
    creation_timestamp      timestamp   default now(),
    creation_user           varchar(50) default "current_user"()                                    not null,
    change_timestamp        timestamp   default now(),
    change_user             varchar(50) default "current_user"()                                    not null
);

alter table cofk_union_relationship
    owner to postgres;

create index cofk_union_relationship_left_idx
    on cofk_union_relationship (left_table_name, left_id_value, relationship_type);

create index cofk_union_relationship_right_idx
    on cofk_union_relationship (right_table_name, right_id_value, relationship_type);

create trigger cofk_union_relationship_trg_audit_del
    before delete
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_audit_any();

create trigger cofk_union_relationship_trg_audit_ins
    after insert
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_audit_any();

create trigger cofk_union_relationship_trg_audit_upd
    after update
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_audit_any();

create trigger cofk_union_relationship_trg_cascade02_del
    after delete
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_cascade02_rel_changes();

create trigger cofk_union_relationship_trg_cascade02_ins
    after insert
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_cascade02_rel_changes();

create trigger cofk_union_relationship_trg_cascade02_upd
    after update
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_union_cascade02_rel_changes();

create trigger cofk_union_relationship_trg_set_change_cols
    before update
    on cofk_union_relationship
    for each row
    execute procedure dbf_cofk_set_change_cols();

alter table cofk_union_audit_relationship
    alter column audit_id set default nextval('cofk_union_audit_id_seq'::regclass);

alter table cofk_union_audit_relationship
alter column change_timestamp type timestamp using change_timestamp::timestamp;

alter table cofk_union_audit_relationship
    alter column change_user set default "current_user"();

alter table cofk_union_manifestation
    add constraint cofk_chk_union_manifestation_creation_date_approx
        check ((manifestation_creation_date_approx = 0) OR (manifestation_creation_date_approx = 1));

alter table cofk_union_manifestation
    add constraint cofk_chk_union_manifestation_creation_date_inferred
        check ((manifestation_creation_date_inferred = 0) OR (manifestation_creation_date_inferred = 1));

alter table cofk_union_manifestation
    add constraint cofk_chk_union_manifestation_creation_date_uncertain
        check ((manifestation_creation_date_uncertain = 0) OR (manifestation_creation_date_uncertain = 1));

create trigger cofk_union_manifestation_trg_cascade03_del
    after delete
    on cofk_union_manifestation
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_manifestation_trg_cascade03_ins
    after insert
    on cofk_union_manifestation
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_manifestation_trg_cascade03_upd
    after update
    on cofk_union_manifestation
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_manifestation_trg_set_change_cols
    before update
    on cofk_union_manifestation
    for each row
    execute procedure dbf_cofk_set_change_cols();

create table cofk_union_person_summary
(
    iperson_id                       integer           not null
        primary key
        constraint cofk_union_fk_person_summary
            references cofk_union_person (iperson_id)
            on delete cascade,
    other_details_summary            text,
    other_details_summary_searchable text,
    sent                             integer default 0 not null,
    recd                             integer default 0 not null,
    all_works                        integer default 0 not null,
    mentioned                        integer default 0 not null,
    role_categories                  text,
    images                           text
);

alter table cofk_union_person_summary
    owner to postgres;

create trigger cofk_union_publication_trg_set_change_cols
    before update
    on cofk_union_publication
    for each row
    execute procedure dbf_cofk_set_change_cols();

create trigger cofk_union_relationship_type_trg_set_change_cols
    before update
    on cofk_union_relationship_type
    for each row
    execute procedure dbf_cofk_set_change_cols();

create trigger cofk_union_resource_trg_cascade03_del
    after delete
    on cofk_union_resource
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_resource_trg_cascade03_ins
    after insert
    on cofk_union_resource
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_resource_trg_cascade03_upd
    after update
    on cofk_union_resource
    for each row
    execute procedure dbf_cofk_union_cascade03_decodes();

create trigger cofk_union_resource_trg_set_change_cols
    before update
    on cofk_union_resource
    for each row
    execute procedure dbf_cofk_set_change_cols();

alter table cofk_user_saved_queries
    add primary key (query_id);

alter table cofk_user_saved_query_selection
    add constraint cofk_fk_user_saved_query_selection_query_id
        foreign key (query_id) references cofk_user_saved_queries;

create table cofk_users
(
    username      varchar(30)                               not null
        primary key,
    pw            text                                      not null
        constraint cofk_users_pw
            check (pw > ''::text),
    surname       varchar(30) default ''::character varying not null,
    forename      varchar(30) default ''::character varying not null,
    failed_logins integer     default 0                     not null,
    login_time    timestamp,
    prev_login    timestamp,
    active        smallint    default 1                     not null
        constraint cofk_users_active
            check ((active = 0) OR (active = 1)),
    email         text
);

alter table cofk_users
    owner to postgres;

create table cofk_sessions
(
    session_id        integer   default nextval('cofk_sessions_session_id_seq'::regclass) not null
        primary key,
    session_timestamp timestamp default now()                                             not null,
    session_code      text
        constraint cofk_uniq_session_code
            unique,
    username          varchar(100)
        constraint cofk_fk_sessions_username
            references cofk_users
);

alter table cofk_sessions
    owner to postgres;

create table cofk_user_roles
(
    username varchar(30) not null
        constraint cofk_fk_user_roles_username
            references cofk_users,
    role_id  integer     not null
        constraint cofk_fk_user_roles_role_id
            references cofk_roles,
    primary key (username, role_id)
);

alter table cofk_user_roles
    owner to postgres;

alter table cofk_user_saved_queries
    add constraint cofk_fk_user_saved_queries_username
        foreign key (username) references cofk_users;

create table copy_cofk_union_queryable_work
(
    iwork_id                   integer,
    work_id                    varchar(100),
    description                text,
    date_of_work_std           date,
    date_of_work_std_year      integer,
    date_of_work_std_month     integer,
    date_of_work_std_day       integer,
    date_of_work_as_marked     varchar(250),
    date_of_work_inferred      smallint,
    date_of_work_uncertain     smallint,
    date_of_work_approx        smallint,
    creators_searchable        text,
    creators_for_display       text,
    authors_as_marked          text,
    notes_on_authors           text,
    authors_inferred           smallint,
    authors_uncertain          smallint,
    addressees_searchable      text,
    addressees_for_display     text,
    addressees_as_marked       text,
    addressees_inferred        smallint,
    addressees_uncertain       smallint,
    places_from_searchable     text,
    places_from_for_display    text,
    origin_as_marked           text,
    origin_inferred            smallint,
    origin_uncertain           smallint,
    places_to_searchable       text,
    places_to_for_display      text,
    destination_as_marked      text,
    destination_inferred       smallint,
    destination_uncertain      smallint,
    manifestations_searchable  text,
    manifestations_for_display text,
    abstract                   text,
    keywords                   text,
    people_mentioned           text,
    images                     text,
    related_resources          text,
    language_of_work           varchar(255),
    work_is_translation        smallint,
    flags                      text,
    edit_status                varchar(3),
    general_notes              text,
    original_catalogue         varchar(100),
    accession_code             varchar(1000),
    work_to_be_deleted         smallint,
    change_timestamp           timestamp,
    change_user                varchar(50),
    drawer                     varchar(50),
    editors_notes              text,
    manifestation_type         varchar(50),
    original_notes             text,
    relevant_to_cofk           varchar(1),
    subjects                   text
);

alter table copy_cofk_union_queryable_work
    owner to postgres;

create table pro_activity
(
    id                    integer   default nextval('pro_id_activity'::regclass) not null
        primary key,
    activity_type_id      text,
    activity_name         text,
    activity_description  text,
    date_type             text,
    date_from_year        text,
    date_from_month       text,
    date_from_day         text,
    date_from_uncertainty text,
    date_to_year          text,
    date_to_month         text,
    date_to_day           text,
    date_to_uncertainty   text,
    notes_used            text,
    additional_notes      text,
    creation_timestamp    timestamp default now(),
    creation_user         text,
    change_timestamp      timestamp default now(),
    change_user           text,
    event_label           text
);

comment on table pro_activity is 'prosopographical activity';

alter table pro_activity
    owner to cofktanya;

drop table django_session;

create table pro_activity_relation
(
    id                       integer default nextval('pro_id_activity_relation'::regclass) not null
        primary key,
    meta_activity_id         integer,
    filename                 text                                                          not null,
    spreadsheet_row          integer                                                       not null,
    combined_spreadsheet_row integer                                                       not null
);

comment on table pro_activity_relation is 'mapping for related prosopography events';

alter table pro_activity_relation
    owner to cofktanya;

alter table cofk_collect_status
    alter column status_id drop default;

alter table cofk_collect_status
alter column editable type smallint using editable::smallint;

create table pro_assertion
(
    id                 integer   default nextval('pro_id_assertion'::regclass) not null
        primary key,
    assertion_type     text,
    assertion_id       text,
    source_id          text,
    source_description text,
    change_timestamp   timestamp default now()
);

alter table pro_assertion
    owner to cofktanya;

alter table cofk_collect_tool_user
    alter column tool_user_id set default nextval('cofk_collect_tool_user_id_seq'::regclass);

drop index cofk_collect_tool_user_tool_user_email_6eb2893b_like;

alter table cofk_collect_tool_user
drop constraint cofk_collect_tool_user_tool_user_email_key;

alter table cofk_collect_upload
    alter column upload_id set default nextval('cofk_collect_upload_id_seq'::regclass);

alter table cofk_collect_upload
drop column upload_file;

alter table cofk_collect_upload
    alter column upload_status set not null;

-- column reordering is not supported cofk_collect_upload.upload_status

alter table cofk_collect_upload
alter column upload_timestamp type timestamp using upload_timestamp::timestamp;

drop index cofk_collect_upload_upload_status_b576aaa0;

alter table cofk_collect_upload
drop constraint cofk_collect_upload_upload_status_b576aaa0_fk_cofk_coll;

create table pro_ingest_map_v2
(
    relationship     text,
    mapping          text,
    s_event_category text,
    s_event_type     text,
    s_role           text,
    p_event_category text,
    p_event_type     text,
    p_role           text
);

alter table pro_ingest_map_v2
    owner to cofktanya;

create table pro_ingest_v8
(
    event_category      text,
    event_type          text,
    event_name          text,
    pp_i                text,
    pp_name             text,
    pp_role             text,
    sp_i                text,
    sp_name             text,
    sp_type             text,
    sp_role             text,
    df_year             text,
    df_month            text,
    df_day              text,
    df_uncertainty      text,
    dt_year             text,
    dt_month            text,
    dt_day              text,
    dt_uncertainty      text,
    date_type           text,
    location_i          text,
    location_detail     text,
    location_city       text,
    location_region     text,
    location_country    text,
    location_type       text,
    ts_abbrev           text,
    ts_detail           text,
    editor              text,
    noted_used          text,
    add_notes           text,
    filename            text,
    spreadsheet_row_id  text,
    combined_csv_row_id text
);

alter table pro_ingest_v8
    owner to cofktanya;

alter table cofk_collect_work
    alter column original_calendar set not null;

-- column reordering is not supported cofk_collect_work.union_iwork_id

-- column reordering is not supported cofk_collect_work.upload_id

alter table cofk_collect_work
    alter column upload_status set not null;

-- column reordering is not supported cofk_collect_work.upload_status

-- column reordering is not supported cofk_collect_work.work_id

drop index cofk_collect_work_union_iwork_id_f813adfc;

drop index cofk_collect_work_upload_id_0802dc06;

drop index cofk_collect_work_upload_status_27f03bb2;

drop index cofk_collect_work_work_id_e477222a;

drop index cofk_collect_work_work_id_e477222a_like;

alter table cofk_collect_work
drop constraint cofk_collect_work_upload_id_iwork_id_4d833f3d_uniq;

alter table cofk_collect_work
drop constraint cofk_collect_work_union_iwork_id_f813adfc_fk_cofk_unio;

alter table cofk_union_work
drop constraint cofk_union_work_iwork_id_key;

alter table cofk_collect_work
drop constraint cofk_collect_work_upload_id_0802dc06_fk_cofk_coll;

alter table cofk_collect_work
drop constraint cofk_collect_work_work_id_e477222a_fk_cofk_union_work_work_id;

alter table cofk_collect_work
drop constraint cofk_collect_work_upload_status_27f03bb2_fk_cofk_coll;

create table pro_ingest_v8_toreview
(
    event_category      text,
    event_type          text,
    event_name          text,
    pp_i                text,
    pp_name             text,
    pp_role             text,
    sp_i                text,
    sp_name             text,
    sp_type             text,
    sp_role             text,
    df_year             text,
    df_month            text,
    df_day              text,
    df_uncertainty      text,
    dt_year             text,
    dt_month            text,
    dt_day              text,
    dt_uncertainty      text,
    date_type           text,
    location_i          text,
    location_detail     text,
    location_city       text,
    location_region     text,
    location_country    text,
    location_type       text,
    ts_abbrev           text,
    ts_detail           text,
    editor              text,
    noted_used          text,
    add_notes           text,
    filename            text,
    spreadsheet_row_id  text,
    combined_csv_row_id text
);

alter table pro_ingest_v8_toreview
    owner to cofktanya;

create table pro_location
(
    id               integer   default nextval('pro_id_location'::regclass) not null
        primary key,
    location_id      text,
    change_timestamp timestamp default now(),
    activity_id      integer
);

alter table pro_location
    owner to cofktanya;

alter table cofk_collect_tool_session
    alter column session_id set default nextval('cofk_sessions_session_id_seq'::regclass);

alter table cofk_collect_tool_session
alter column session_timestamp type timestamp using session_timestamp::timestamp;

alter table cofk_collect_tool_session
alter column username type varchar(100) using username::varchar(100);

drop index cofk_collect_tool_session_session_code_dd423eca_like;

drop index cofk_collect_tool_session_username_77e0c349;

alter table cofk_collect_tool_session
drop constraint cofk_collect_tool_session_session_code_key;

alter table cofk_collect_tool_session
drop constraint cofk_collect_tool_se_username_77e0c349_fk_cofk_coll;

create table pro_people_check
(
    person_name text,
    iperson_id  text
);

alter table pro_people_check
    owner to cofktanya;

create table pro_primary_person
(
    id               integer   default nextval('pro_id_primary_person'::regclass) not null
        primary key,
    person_id        text,
    change_timestamp timestamp default now(),
    activity_id      integer
);

alter table pro_primary_person
    owner to cofktanya;

-- column reordering is not supported cofk_collect_person.upload_id

alter table cofk_collect_person
    alter column iperson_id set not null;

-- column reordering is not supported cofk_collect_person.union_iperson_id

drop index cofk_collect_person_union_iperson_id_c047cdb3;

drop index cofk_collect_person_upload_id_4ce05075;

alter table cofk_collect_person
drop constraint cofk_collect_person_upload_id_iperson_id_09e71047_uniq;

alter table cofk_collect_person
drop constraint cofk_collect_person_union_iperson_id_c047cdb3_fk_cofk_unio;

alter table cofk_union_person
drop constraint cofk_union_person_iperson_id_key;

alter table cofk_collect_person
drop constraint cofk_collect_person_upload_id_4ce05075_fk_cofk_coll;

create table pro_relationship
(
    id               integer   default nextval('pro_id_relationship'::regclass) not null
        primary key,
    subject_id       text,
    subject_type     text,
    subject_role_id  text,
    relationship_id  text,
    object_id        text,
    object_type      text,
    object_role_id   text,
    change_timestamp timestamp default now(),
    activity_id      integer
);

alter table pro_relationship
    owner to cofktanya;

-- column reordering is not supported cofk_collect_location.union_location_id

-- column reordering is not supported cofk_collect_location.upload_id

drop index cofk_collect_location_union_location_id_1da76575;

drop index cofk_collect_location_upload_id_02d01558;

alter table cofk_collect_location
drop constraint cofk_collect_location_upload_id_location_id_50c243da_uniq;

alter table cofk_collect_location
drop constraint cofk_collect_locatio_union_location_id_1da76575_fk_cofk_unio;

alter table cofk_collect_location
drop constraint cofk_collect_locatio_upload_id_02d01558_fk_cofk_coll;

create table pro_role_in_activity
(
    id               integer   default nextval('pro_id_role_in_activity'::regclass) not null
        primary key,
    entity_type      text,
    entity_id        text,
    role_id          text,
    change_timestamp timestamp default now(),
    activity_id      integer
);

alter table pro_role_in_activity
    owner to cofktanya;

-- column reordering is not supported cofk_collect_institution.union_institution_id

-- column reordering is not supported cofk_collect_institution.upload_id

drop index cofk_collect_institution_union_institution_id_4b3395e1;

drop index cofk_collect_institution_upload_id_a28243e5;

alter table cofk_collect_institution
drop constraint cofk_collect_institution_upload_id_institution_id_c3e31e30_uniq;

alter table cofk_collect_institution
drop constraint cofk_collect_institu_union_institution_id_4b3395e1_fk_cofk_unio;

alter table cofk_collect_institution
drop constraint cofk_collect_institu_upload_id_a28243e5_fk_cofk_coll;

create table pro_textual_source
(
    id                         integer   default nextval('pro_id_textual_source'::regclass) not null
        primary key,
    author                     text,
    title                      text,
    "chapterArticleTitle"      text,
    "volumeSeriesNumber"       text,
    "issueNumber"              text,
    "pageNumber"               text,
    editor                     text,
    "placePublication"         text,
    "datePublication"          text,
    "urlResource"              text,
    abbreviation               text,
    "fullBibliographicDetails" text,
    edition                    text,
    "reprintFacsimile"         text,
    repository                 text,
    creation_user              text,
    creation_timestamp         timestamp default now(),
    change_user                text,
    change_timestamp           timestamp default now()
);

alter table pro_textual_source
    owner to cofktanya;

-- column reordering is not supported cofk_collect_image_of_manif.upload_id

drop index cofk_collect_image_of_manif_upload_id_7b16ccf2;

alter table cofk_collect_image_of_manif
drop constraint cofk_collect_image_of_manif_pkey;

alter table cofk_collect_image_of_manif
drop column id;

alter table cofk_collect_image_of_manif
drop constraint cofk_collect_image_o_upload_id_7b16ccf2_fk_cofk_coll;

-- column reordering is not supported cofk_collect_work_summary.upload_id

drop index cofk_collect_work_summary_upload_id_e54eb198;

alter table cofk_collect_work_summary
drop constraint cofk_collect_work_summary_pkey;

alter table cofk_collect_work_summary
    add primary key (upload_id, work_id_in_tool);

alter table cofk_collect_work_summary
drop column id;

alter table cofk_collect_work_summary
drop constraint cofk_collect_work_summary_work_id_in_tool_id_key;

alter table cofk_collect_work_summary
drop constraint cofk_collect_work_summar_upload_id_work_id_in_too_f18e0c99_uniq;

alter table cofk_collect_work_summary
drop constraint cofk_collect_work_su_upload_id_e54eb198_fk_cofk_coll;

alter table cofk_collect_work_summary
drop constraint cofk_collect_work_su_work_id_in_tool_id_c7780bf7_fk_cofk_coll;

alter table cofk_collect_work_summary
drop column work_id_in_tool_id;

alter table cofk_collect_work_resource
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_work_resource.iwork_id

-- column reordering is not supported cofk_collect_work_resource.upload_id

drop index cofk_collect_work_resource_iwork_id_cdd7a90c;

drop index cofk_collect_work_resource_upload_id_63e6e9b1;

alter table cofk_collect_work_resource
drop constraint cofk_collect_work_resource_pkey;

alter table cofk_collect_work_resource
    add primary key (upload_id, iwork_id, resource_id);

alter table cofk_collect_work_resource
drop column id;

alter table cofk_collect_work_resource
drop constraint cofk_collect_work_resour_upload_id_iwork_id_resou_af123383_uniq;

alter table cofk_collect_work_resource
drop constraint cofk_collect_work_re_iwork_id_cdd7a90c_fk_cofk_coll;

alter table cofk_collect_work_resource
drop constraint cofk_collect_work_re_upload_id_63e6e9b1_fk_cofk_coll;

-- column reordering is not supported cofk_collect_subject_of_work.upload_id

alter table cofk_collect_subject_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_subject_of_work.iwork_id

drop index cofk_collect_subject_of_work_subject_id_ab4a8812;

drop index cofk_collect_subject_of_work_upload_id_9a423a03;

drop index cofk_collect_subject_of_work_iwork_id_0afa06ad;

alter table cofk_collect_subject_of_work
drop constraint cofk_collect_subject_of_work_pkey;

alter table cofk_collect_subject_of_work
    add primary key (upload_id, iwork_id, subject_of_work_id);

alter table cofk_collect_subject_of_work
drop column id;

alter table cofk_collect_subject_of_work
drop constraint cofk_collect_subject_subject_id_ab4a8812_fk_cofk_unio;

alter table cofk_collect_subject_of_work
drop constraint cofk_collect_subject_upload_id_9a423a03_fk_cofk_coll;

alter table cofk_collect_subject_of_work
drop constraint cofk_collect_subject_iwork_id_0afa06ad_fk_cofk_coll;

-- column reordering is not supported cofk_collect_place_mentioned_in_work.upload_id

alter table cofk_collect_place_mentioned_in_work
alter column location_id type integer using location_id::integer;

-- column reordering is not supported cofk_collect_place_mentioned_in_work.location_id

alter table cofk_collect_place_mentioned_in_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_place_mentioned_in_work.iwork_id

drop index cofk_collect_place_mentioned_in_work_upload_id_a787ad2a;

drop index cofk_collect_place_mentioned_in_work_iwork_id_2a9da84e;

drop index cofk_collect_place_mentioned_in_work_location_id_4ccc1dd5;

alter table cofk_collect_place_mentioned_in_work
drop constraint cofk_collect_place_mentioned_in_work_pkey;

alter table cofk_collect_place_mentioned_in_work
    add primary key (upload_id, iwork_id, mention_id);

alter table cofk_collect_place_mentioned_in_work
drop column id;

alter table cofk_collect_place_mentioned_in_work
drop constraint cofk_collect_place_m_upload_id_a787ad2a_fk_cofk_coll;

alter table cofk_collect_place_mentioned_in_work
drop constraint cofk_collect_place_m_iwork_id_2a9da84e_fk_cofk_coll;

alter table cofk_collect_place_mentioned_in_work
drop constraint cofk_collect_place_m_location_id_4ccc1dd5_fk_cofk_coll;

-- column reordering is not supported cofk_collect_person_resource.upload_id

drop index cofk_collect_person_resource_upload_id_cb3e072e;

alter table cofk_collect_person_resource
drop constraint cofk_collect_person_resource_pkey;

alter table cofk_collect_person_resource
    add primary key (upload_id, resource_id);

alter table cofk_collect_person_resource
drop column id;

alter table cofk_collect_person_resource
drop constraint cofk_collect_person_reso_upload_id_resource_id_28d43830_uniq;

alter table cofk_collect_person_resource
drop constraint cofk_collect_person__upload_id_cb3e072e_fk_cofk_coll;

alter table cofk_collect_person_mentioned_in_work
alter column iperson_id type integer using iperson_id::integer;

-- column reordering is not supported cofk_collect_person_mentioned_in_work.iperson_id

alter table cofk_collect_person_mentioned_in_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_person_mentioned_in_work.iwork_id

-- column reordering is not supported cofk_collect_person_mentioned_in_work.upload_id

drop index cofk_collect_person_mentioned_in_work_iperson_id_900811a8;

drop index cofk_collect_person_mentioned_in_work_iwork_id_a9c68e50;

drop index cofk_collect_person_mentioned_in_work_upload_id_cd3493b7;

alter table cofk_collect_person_mentioned_in_work
drop constraint cofk_collect_person_mentioned_in_work_pkey;

alter table cofk_collect_person_mentioned_in_work
    add primary key (upload_id, iwork_id, mention_id);

alter table cofk_collect_person_mentioned_in_work
drop column id;

alter table cofk_collect_person_mentioned_in_work
drop constraint cofk_collect_person_ment_upload_id_iwork_id_menti_f1e730b0_uniq;

alter table cofk_collect_person_mentioned_in_work
drop constraint cofk_collect_person__iperson_id_900811a8_fk_cofk_coll;

alter table cofk_collect_person_mentioned_in_work
drop constraint cofk_collect_person__iwork_id_a9c68e50_fk_cofk_coll;

alter table cofk_collect_person_mentioned_in_work
drop constraint cofk_collect_person__upload_id_cd3493b7_fk_cofk_coll;

alter table cofk_collect_origin_of_work
alter column location_id type integer using location_id::integer;

-- column reordering is not supported cofk_collect_origin_of_work.location_id

alter table cofk_collect_origin_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_origin_of_work.iwork_id

-- column reordering is not supported cofk_collect_origin_of_work.upload_id

drop index cofk_collect_origin_of_work_iwork_id_98a4e2d3;

drop index cofk_collect_origin_of_work_location_id_713265bb;

drop index cofk_collect_origin_of_work_upload_id_f6a4ff5a;

alter table cofk_collect_origin_of_work
drop constraint cofk_collect_origin_of_work_pkey;

alter table cofk_collect_origin_of_work
    add primary key (upload_id, iwork_id, origin_id);

alter table cofk_collect_origin_of_work
drop column id;

alter table cofk_collect_origin_of_work
drop constraint cofk_collect_origin_of_w_upload_id_iwork_id_origi_5dc07a79_uniq;

alter table cofk_collect_origin_of_work
drop constraint cofk_collect_origin__iwork_id_98a4e2d3_fk_cofk_coll;

alter table cofk_collect_origin_of_work
drop constraint cofk_collect_origin__location_id_713265bb_fk_cofk_coll;

alter table cofk_collect_origin_of_work
drop constraint cofk_collect_origin__upload_id_f6a4ff5a_fk_cofk_coll;

-- column reordering is not supported cofk_collect_occupation_of_person.upload_id

drop index cofk_collect_occupation_of_person_occupation_id_e7789f0e;

drop index cofk_collect_occupation_of_person_upload_id_4c650320;

alter table cofk_collect_occupation_of_person
drop constraint cofk_collect_occupation_of_person_pkey;

alter table cofk_collect_occupation_of_person
    add primary key (upload_id, occupation_of_person_id);

alter table cofk_collect_occupation_of_person
drop column id;

alter table cofk_collect_occupation_of_person
drop constraint cofk_collect_occupation__upload_id_occupation_of__54441db1_uniq;

alter table cofk_collect_occupation_of_person
drop constraint cofk_collect_occupat_occupation_id_e7789f0e_fk_cofk_unio;

alter table cofk_collect_occupation_of_person
drop constraint cofk_collect_occupat_upload_id_4c650320_fk_cofk_coll;

alter table cofk_collect_manifestation
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_manifestation.iwork_id

alter table cofk_collect_manifestation
alter column repository_id type integer using repository_id::integer;

-- column reordering is not supported cofk_collect_manifestation.repository_id

-- column reordering is not supported cofk_collect_manifestation.union_manifestation_id

-- column reordering is not supported cofk_collect_manifestation.upload_id

drop index cofk_collect_manifestation_iwork_id_fcdf68f2;

drop index cofk_collect_manifestation_repository_id_5685a307;

drop index cofk_collect_manifestation_union_manifestation_id_1fb7024b;

drop index cofk_collect_manifestation_union_manifestation_id_1fb7024b_like;

drop index cofk_collect_manifestation_upload_id_1f97a779;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifestation_pkey;

alter table cofk_collect_manifestation
    add primary key (upload_id, iwork_id, manifestation_id);

alter table cofk_collect_image_of_manif
    add constraint cofk_collect_image_of_manif_fk_manifestation_id
        foreign key (upload_id, iwork_id, manifestation_id) references cofk_collect_manifestation;

alter table cofk_collect_manifestation
drop column id;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifestati_upload_id_iwork_id_manif_80b93ddf_uniq;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifes_iwork_id_fcdf68f2_fk_cofk_coll;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifes_repository_id_5685a307_fk_cofk_coll;

alter table cofk_collect_institution
drop constraint cofk_collect_institution_pkey;

alter table cofk_collect_institution
    add primary key (upload_id, institution_id);

alter table cofk_collect_institution_resource
    add constraint cofk_collect_institution_resource_fk_institution_id
        foreign key (upload_id, institution_id) references cofk_collect_institution;

alter table cofk_collect_manifestation
    add constraint cofk_collect_manifestation_fk_repos
        foreign key (upload_id, repository_id) references cofk_collect_institution;

alter table cofk_collect_institution
drop column id;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifes_union_manifestation__1fb7024b_fk_cofk_unio;

alter table cofk_collect_manifestation
drop constraint cofk_collect_manifes_upload_id_1f97a779_fk_cofk_coll;

-- column reordering is not supported cofk_collect_location_resource.upload_id

drop index cofk_collect_location_resource_upload_id_a92a9607;

alter table cofk_collect_location_resource
drop constraint cofk_collect_location_resource_pkey;

alter table cofk_collect_location_resource
    add primary key (upload_id, resource_id);

alter table cofk_collect_location_resource
drop column id;

alter table cofk_collect_location_resource
drop constraint cofk_collect_location_re_upload_id_resource_id_8500f73f_uniq;

alter table cofk_collect_location_resource
drop constraint cofk_collect_locatio_upload_id_a92a9607_fk_cofk_coll;

-- column reordering is not supported cofk_collect_language_of_work._id

alter table cofk_collect_language_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_language_of_work.upload_id

drop index cofk_collect_language_of_work_iwork_id_eadca89e;

drop index cofk_collect_language_of_work_language_code_b815d6ff;

drop index cofk_collect_language_of_work_language_code_b815d6ff_like;

drop index cofk_collect_language_of_work_upload_id_73bfa507;

alter table cofk_collect_language_of_work
drop constraint cofk_collect_language_of_work_pkey;

alter table cofk_collect_language_of_work
    add primary key (upload_id, iwork_id, language_of_work_id);

alter table cofk_collect_language_of_work
drop column id;

alter table cofk_collect_language_of_work
drop constraint cofk_collect_language_of_upload_id_iwork_id_langu_17f94255_uniq;

alter table cofk_collect_language_of_work
drop constraint cofk_collect_languag_iwork_id_eadca89e_fk_cofk_coll;

alter table cofk_collect_language_of_work
drop constraint cofk_collect_languag_language_code_b815d6ff_fk_iso_639_l;

alter table cofk_collect_language_of_work
drop constraint cofk_collect_languag_upload_id_73bfa507_fk_cofk_coll;

-- column reordering is not supported cofk_collect_institution_resource.upload_id

drop index cofk_collect_institution_resource_upload_id_32dbe7da;

alter table cofk_collect_institution_resource
drop constraint cofk_collect_institution_resource_pkey;

alter table cofk_collect_institution_resource
    add primary key (upload_id, resource_id);

alter table cofk_collect_institution_resource
drop column id;

alter table cofk_collect_institution_resource
drop constraint cofk_collect_institution_upload_id_resource_id_fdb3f098_uniq;

alter table cofk_collect_institution_resource
drop constraint cofk_collect_institu_upload_id_32dbe7da_fk_cofk_coll;

alter table cofk_collect_destination_of_work
alter column location_id type integer using location_id::integer;

-- column reordering is not supported cofk_collect_destination_of_work.location_id

alter table cofk_collect_destination_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_destination_of_work.iwork_id

-- column reordering is not supported cofk_collect_destination_of_work.upload_id

drop index cofk_collect_destination_of_work_iwork_id_e6f7d1df;

drop index cofk_collect_destination_of_work_location_id_df4507b1;

drop index cofk_collect_destination_of_work_upload_id_90b3cf61;

alter table cofk_collect_destination_of_work
drop constraint cofk_collect_destination_of_work_pkey;

alter table cofk_collect_destination_of_work
    add primary key (upload_id, iwork_id, destination_id);

alter table cofk_collect_destination_of_work
drop column id;

alter table cofk_collect_destination_of_work
drop constraint cofk_collect_destination_upload_id_iwork_id_desti_d398f1ac_uniq;

alter table cofk_collect_destination_of_work
drop constraint cofk_collect_destina_iwork_id_e6f7d1df_fk_cofk_coll;

alter table cofk_collect_destination_of_work
drop constraint cofk_collect_destina_location_id_df4507b1_fk_cofk_coll;

alter table cofk_collect_location
drop constraint cofk_collect_location_pkey;

alter table cofk_collect_location
    add primary key (upload_id, location_id);

alter table cofk_collect_destination_of_work
    add constraint cofk_collect_destination_of_work_fk_location_id
        foreign key (upload_id, location_id) references cofk_collect_location;

alter table cofk_collect_location_resource
    add constraint cofk_collect_location_resource_fk_location_id
        foreign key (upload_id, location_id) references cofk_collect_location;

alter table cofk_collect_origin_of_work
    add constraint cofk_collect_origin_of_work_fk_location_id
        foreign key (upload_id, location_id) references cofk_collect_location;

alter table cofk_collect_place_mentioned_in_work
    add constraint cofk_collect_place_mentioned_in_work_fk_location_id
        foreign key (upload_id, location_id) references cofk_collect_location;

alter table cofk_collect_work
    add constraint cofk_collect_destination_of_work_fk_location_id
        foreign key (upload_id, destination_id) references cofk_collect_location;

alter table cofk_collect_work
    add constraint cofk_collect_origin_of_work_fk_location_id
        foreign key (upload_id, origin_id) references cofk_collect_location;

alter table cofk_collect_location
drop column id;

alter table cofk_collect_destination_of_work
drop constraint cofk_collect_destina_upload_id_90b3cf61_fk_cofk_coll;

alter table cofk_collect_author_of_work
alter column iperson_id type integer using iperson_id::integer;

-- column reordering is not supported cofk_collect_author_of_work.iperson_id

alter table cofk_collect_author_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_author_of_work.iwork_id

-- column reordering is not supported cofk_collect_author_of_work.upload_id

drop index cofk_collect_author_of_work_iperson_id_965dd0b1;

drop index cofk_collect_author_of_work_iwork_id_1699d182;

drop index cofk_collect_author_of_work_upload_id_33824bf3;

alter table cofk_collect_author_of_work
drop constraint cofk_collect_author_of_work_pkey;

alter table cofk_collect_author_of_work
    add primary key (upload_id, iwork_id, author_id);

alter table cofk_collect_author_of_work
drop column id;

alter table cofk_collect_author_of_work
drop constraint cofk_collect_author_of_w_upload_id_iwork_id_autho_6e375d91_uniq;

alter table cofk_collect_author_of_work
drop constraint cofk_collect_author__iperson_id_965dd0b1_fk_cofk_coll;

alter table cofk_collect_author_of_work
drop constraint cofk_collect_author__iwork_id_1699d182_fk_cofk_coll;

alter table cofk_collect_author_of_work
drop constraint cofk_collect_author__upload_id_33824bf3_fk_cofk_coll;

alter table cofk_collect_addressee_of_work
alter column iperson_id type integer using iperson_id::integer;

-- column reordering is not supported cofk_collect_addressee_of_work.iperson_id

alter table cofk_collect_addressee_of_work
alter column iwork_id type integer using iwork_id::integer;

-- column reordering is not supported cofk_collect_addressee_of_work.iwork_id

-- column reordering is not supported cofk_collect_addressee_of_work.upload_id

drop index cofk_collect_addressee_of_work_iperson_id_10330dc7;

drop index cofk_collect_addressee_of_work_iwork_id_86df0a49;

drop index cofk_collect_addressee_of_work_upload_id_506529bb;

alter table cofk_collect_addressee_of_work
drop constraint cofk_collect_addressee_of_work_pkey;

alter table cofk_collect_addressee_of_work
    add primary key (upload_id, iwork_id, addressee_id);

alter table cofk_collect_addressee_of_work
drop column id;

alter table cofk_collect_addressee_of_work
drop constraint cofk_collect_addressee_o_upload_id_iwork_id_addre_9314246f_uniq;

alter table cofk_collect_addressee_of_work
drop constraint cofk_collect_address_iperson_id_10330dc7_fk_cofk_coll;

alter table cofk_collect_person
drop constraint cofk_collect_person_pkey;

alter table cofk_collect_person
    add primary key (upload_id, iperson_id);

alter table cofk_collect_addressee_of_work
    add constraint cofk_collect_addressee_of_work_fk_iperson_id
        foreign key (upload_id, iperson_id) references cofk_collect_person;

alter table cofk_collect_author_of_work
    add constraint cofk_collect_author_of_work_fk_iperson_id
        foreign key (upload_id, iperson_id) references cofk_collect_person;

alter table cofk_collect_occupation_of_person
    add constraint cofk_collect_occupation_of_person_fk_iperson_id
        foreign key (upload_id, iperson_id) references cofk_collect_person;

alter table cofk_collect_person_mentioned_in_work
    add constraint cofk_collect_person_mentioned_in_work_fk_iperson_id
        foreign key (upload_id, iperson_id) references cofk_collect_person;

alter table cofk_collect_person_resource
    add constraint cofk_collect_person_resource_fk_iperson_id
        foreign key (upload_id, iperson_id) references cofk_collect_person;

alter table cofk_collect_person
drop column id;

alter table cofk_collect_addressee_of_work
drop constraint cofk_collect_address_iwork_id_86df0a49_fk_cofk_coll;

alter table cofk_collect_work
drop constraint cofk_collect_work_pkey;

alter table cofk_collect_work
    add primary key (upload_id, iwork_id);

alter table cofk_collect_addressee_of_work
    add constraint cofk_collect_addressee_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_author_of_work
    add constraint cofk_collect_author_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_destination_of_work
    add constraint cofk_collect_destination_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_language_of_work
    add constraint cofk_collect_language_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_manifestation
    add constraint cofk_collect_manifestation_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_origin_of_work
    add constraint cofk_collect_origin_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_person_mentioned_in_work
    add constraint cofk_collect_person_mentioned_in_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_place_mentioned_in_work
    add constraint cofk_collect_place_mentioned_in_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_subject_of_work
    add constraint cofk_collect_subject_of_work_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_work_resource
    add constraint cofk_collect_work_resource_fk_iwork_id
        foreign key (upload_id, iwork_id) references cofk_collect_work;

alter table cofk_collect_work_summary
    add constraint cofk_collect_work_fk_work_id_in_tool
        foreign key (upload_id, work_id_in_tool) references cofk_collect_work;

alter table cofk_collect_work
drop column id;

alter table cofk_collect_addressee_of_work
drop constraint cofk_collect_address_upload_id_506529bb_fk_cofk_coll;

